"""
The MIT License (MIT)

Copyright (c) 2015-present Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

import asyncio
import copy
import datetime
import inspect
import logging
import weakref
from collections import deque, OrderedDict
from typing import (
    Dict,
    Optional,
    TYPE_CHECKING,
    Union,
    Callable,
    Any,
    List,
    TypeVar,
    Coroutine,
    Tuple,
    Deque,
    Literal,
    overload,
    Sequence,
)

from discord_protos import UserSettingsType

from . import utils
from .activity import Session, create_activity, ActivityTypes
from .application import IntegrationApplication
from .channel import *
from .channel import _private_channel_factory
from .emoji import Emoji
from .enums import (
    ReadStateType,
    Status,
)
from .errors import ClientException, InvalidData
from .flags import MemberCacheFlags
from .guild import ApplicationCommandCounts, Guild
from .interactions import Interaction
from .message import Message
from .modal import Modal
from .raw_models import *
from .read_state import ReadState
from .settings import UserSettings
from .user import User, ClientUser

if TYPE_CHECKING:
    from typing_extensions import Self

    from .message import MessageableChannel
    from .guild import GuildChannel
    from .http import HTTPClient
    from .client import Client

    from .types.snowflake import Snowflake
    from .types.application import (
        IntegrationApplication as IntegrationApplicationPayload,
    )
    from .types.channel import DMChannel as DMChannelPayload
    from .types.user import User as UserPayload, PartialUser as PartialUserPayload
    from .types.emoji import Emoji as EmojiPayload
    from .types.guild import BaseGuild as BaseGuildPayload, Guild as GuildPayload
    from .types.message import (
        Message as MessagePayload,
        MessageSearchResult as MessageSearchResultPayload,
        PartialMessage as PartialMessagePayload,
    )
    from .types import gateway as gw
    from .types.activity import ClientStatus as ClientStatusPayload

    T = TypeVar("T")
    PrivateChannel = Union[DMChannel]
    Channel = Union[GuildChannel, PrivateChannel, PartialMessageable]

MISSING = utils.MISSING
_log = logging.getLogger(__name__)


class ClientStatus:
    __slots__ = ("status", "desktop", "mobile", "web")

    def __init__(
        self,
        status: Optional[str] = None,
        data: Optional[ClientStatusPayload] = None,
        /,
    ) -> None:
        self.status: str = "offline"
        self.desktop: Optional[str] = None
        self.mobile: Optional[str] = None
        self.web: Optional[str] = None

        if status is not None or data is not None:
            self._update(status or "offline", data or {})

    def __repr__(self) -> str:
        attrs = [
            ("status", self.status),
            ("desktop", self.desktop),
            ("mobile", self.mobile),
            ("web", self.web),
        ]
        inner = " ".join("%s=%r" % t for t in attrs)
        return f"<{self.__class__.__name__} {inner}>"

    def _update(self, status: str, data: ClientStatusPayload, /) -> None:
        self.status = status
        self.desktop = data.get("desktop")
        self.mobile = data.get("mobile")
        self.web = data.get("web")

    @classmethod
    def _copy(cls, client_status: Self, /) -> Self:
        self = cls.__new__(cls)  # bypass __init__
        self.status = client_status.status
        self.desktop = client_status.desktop
        self.mobile = client_status.mobile
        self.web = client_status.web
        return self


class Presence:
    __slots__ = ("client_status", "activities", "last_modified")

    def __init__(self, data: gw.BasePresenceUpdate, state: ConnectionState, /) -> None:
        self.client_status: ClientStatus = ClientStatus(
            data["status"], data.get("client_status")
        )
        self.activities: Tuple[ActivityTypes, ...] = tuple(
            create_activity(d, state) for d in data["activities"]
        )
        self.last_modified: Optional[datetime.datetime] = utils.parse_timestamp(
            data.get("last_modified")
        )

    def __repr__(self) -> str:
        attrs = [
            ("client_status", self.client_status),
            ("activities", self.activities),
            ("last_modified", self.last_modified),
        ]
        inner = " ".join("%s=%r" % t for t in attrs)
        return f"<{self.__class__.__name__} {inner}>"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Presence):
            return False
        return (
            self.client_status == other.client_status
            and self.activities == other.activities
        )

    def __ne__(self, other: Any) -> bool:
        if not isinstance(other, Presence):
            return True
        return (
            self.client_status != other.client_status
            or self.activities != other.activities
        )

    def _update(self, data: gw.BasePresenceUpdate, state: ConnectionState, /) -> None:
        self.client_status._update(data["status"], data.get("client_status"))
        self.activities = tuple(create_activity(d, state) for d in data["activities"])
        self.last_modified = (
            utils.parse_timestamp(data.get("last_modified")) or utils.utcnow()
        )

    @classmethod
    def _offline(cls) -> Self:
        self = cls.__new__(cls)  # bypass __init__
        self.client_status = ClientStatus()
        self.activities = ()
        self.last_modified = None
        return self

    @classmethod
    def _copy(cls, presence: Self, /) -> Self:
        self = cls.__new__(cls)  # bypass __init__
        self.client_status = ClientStatus._copy(presence.client_status)
        self.activities = presence.activities
        self.last_modified = presence.last_modified
        return self


class FakeClientPresence(Presence):
    __slots__ = ("_state",)

    def __init__(self, state: ConnectionState, /) -> None:
        self._state = state

    def _update(self, data: gw.PresenceUpdateEvent, state: ConnectionState, /) -> None:
        return

    @property
    def client_status(self) -> ClientStatus:
        state = self._state
        status = str(getattr(state.current_session, "status", "offline"))
        client_status = {
            str(session.client): str(session.status)
            for session in state._sessions.values()
        }
        return ClientStatus(status, client_status)  # type: ignore

    @property
    def activities(self) -> Tuple[ActivityTypes, ...]:
        return getattr(self._state.current_session, "activities", ())

    @property
    def last_modified(self) -> Optional[datetime.datetime]:
        return None


async def logging_coroutine(
    coroutine: Coroutine[Any, Any, T], *, info: str
) -> Optional[T]:
    try:
        await coroutine
    except Exception:
        _log.exception("Exception occurred during %s.", info)


class ConnectionState:
    def __init__(
        self,
        *,
        dispatch: Callable[..., Any],
        handlers: Dict[str, Callable[..., Any]],
        hooks: Dict[str, Callable[..., Coroutine[Any, Any, Any]]],
        http: HTTPClient,
        client: Client,
        **options: Any,
    ) -> None:
        # Set later, after Client.login
        self.loop: asyncio.AbstractEventLoop = utils.MISSING
        self.http: HTTPClient = http
        self.client = client
        self.max_messages: Optional[int] = options.get("max_messages", 1000)
        if self.max_messages is not None and self.max_messages <= 0:
            self.max_messages = 1000

        self.dispatch: Callable[..., Any] = dispatch
        self.handlers: Dict[str, Callable[..., Any]] = handlers
        self.hooks: Dict[str, Callable[..., Coroutine[Any, Any, Any]]] = hooks
        self._ready_task: Optional[asyncio.Task] = None
        self.heartbeat_timeout: float = options.get("heartbeat_timeout", 60.0)

        status = options.get("status", None)
        if status:
            if status is Status.offline:
                status = "invisible"
            else:
                status = str(status)

        self._chunk_guilds: bool = options.get("chunk_guilds_at_startup", True)
        self._request_guilds = options.get("request_guilds", True)

        cache_flags = options.get("member_cache_flags", None)
        if cache_flags is None:
            cache_flags = MemberCacheFlags.all()
        else:
            if not isinstance(cache_flags, MemberCacheFlags):
                raise TypeError(
                    "member_cache_flags parameter must be MemberCacheFlags not"
                    f" {type(cache_flags)!r}"
                )

        self.member_cache_flags: MemberCacheFlags = cache_flags
        self._status: Optional[str] = status

        if cache_flags._empty:
            self.store_user = self.create_user

        self.parsers: Dict[str, Callable[[Any], None]]
        self.parsers = parsers = {}
        for attr, func in inspect.getmembers(self):
            if attr.startswith("parse_"):
                parsers[attr[6:].upper()] = func

        self.clear()

    def clear(self) -> None:
        self.user: Optional[ClientUser] = None
        self._users: weakref.WeakValueDictionary[int, User] = (
            weakref.WeakValueDictionary()
        )
        self.settings: Optional[UserSettings] = None
        self.analytics_token: Optional[str] = None
        self.preferred_rtc_regions: List[str] = []
        self.country_code: Optional[str] = None
        self.api_code_version: int = 0
        self.session_type: Optional[str] = None
        self.auth_session_id: Optional[str] = None
        self.friend_suggestion_count: int = 0
        self.disclose: List[str] = []
        self._emojis: Dict[int, Emoji] = {}
        self._guilds: Dict[int, Guild] = {}

        self._read_states: Dict[int, Dict[int, ReadState]] = {}
        self.read_state_version: int = 0

        self._call_message_cache: Dict[int, Message] = (
            {}
        )  # Hopefully this won't be a memory leak

        self._interaction_cache: Dict[
            Union[int, str], Tuple[int, Optional[str], MessageableChannel]
        ] = {}
        self._interactions: OrderedDict[Union[int, str], Interaction] = (
            OrderedDict()
        )  # LRU of max size 15
        self._private_channels: Dict[int, PrivateChannel] = {}
        self._private_channels_by_user: Dict[int, DMChannel] = {}

        self._guild_presences: Dict[int, Dict[int, Presence]] = {}
        self._presences: Dict[int, Presence] = {}
        self._sessions: Dict[str, Session] = {}

        if self.max_messages is not None:
            self._messages: Optional[Deque[Message]] = deque(maxlen=self.max_messages)
        else:
            self._messages: Optional[Deque[Message]] = None

    def call_handlers(self, key: str, *args: Any, **kwargs: Any) -> None:
        try:
            func = self.handlers[key]
        except KeyError:
            pass
        else:
            func(*args, **kwargs)

    async def call_hooks(self, key: str, *args: Any, **kwargs: Any) -> None:
        try:
            coro = self.hooks[key]
        except KeyError:
            pass
        else:
            await coro(*args, **kwargs)

    async def async_setup(self) -> None:
        pass

    @property
    def session_id(self) -> Optional[str]:
        if self.ws:
            return self.ws.session_id

    @property
    def ws(self):
        return self.client.ws

    @property
    def self_id(self) -> Optional[int]:
        u = self.user
        return u.id if u else None

    @property
    def locale(self) -> str:
        return str(getattr(self.user, "locale", "en-US"))

    @property
    def preferred_rtc_region(self) -> str:
        return (
            self.preferred_rtc_regions[0]
            if self.preferred_rtc_regions
            else "us-central"
        )

    def _add_interaction(self, interaction: Interaction) -> None:
        self._interactions[interaction.id] = interaction
        if len(self._interactions) > 15:
            self._interactions.popitem(last=False)

    def store_user(
        self, data: Union[UserPayload, PartialUserPayload], *, cache: bool = True
    ) -> User:
        # this way is 300% faster than `dict.setdefault`.
        user_id = int(data["id"])
        try:
            return self._users[user_id]
        except KeyError:
            user = User(state=self, data=data)
            if cache:
                self._users[user_id] = user
            return user

    def create_user(
        self, data: Union[UserPayload, PartialUserPayload], cache: bool = False
    ) -> User:
        user_id = int(data["id"])
        if user_id == self.self_id:
            return self.user  # type: ignore
        return User(state=self, data=data)

    def get_user(self, id: int) -> Optional[User]:
        return self._users.get(id)

    def store_emoji(self, guild: Guild, data: EmojiPayload) -> Emoji:
        # The id will be present here
        emoji_id = int(data["id"])  # type: ignore
        emoji = Emoji(guild=guild, state=self, data=data)
        if not self.is_guild_evicted(guild):
            self._emojis[emoji_id] = emoji
        return emoji

    @property
    def guilds(self) -> Sequence[Guild]:
        return utils.SequenceProxy(self._guilds.values())

    def _get_guild(self, guild_id: Optional[int], /) -> Optional[Guild]:
        # The keys of self._guilds are ints
        return self._guilds.get(guild_id)  # type: ignore

    def _get_or_create_unavailable_guild(self, guild_id: int, /) -> Guild:
        return self._guilds.get(guild_id) or Guild._create_unavailable(
            state=self, guild_id=guild_id
        )

    def _add_guild(self, guild: Guild, /) -> None:
        self._guilds[guild.id] = guild

    def _remove_guild(self, guild: Guild, /) -> None:
        self._guilds.pop(guild.id, None)

        for emoji in guild.emojis:
            self._emojis.pop(emoji.id, None)

        del guild

    def create_guild(self, guild: BaseGuildPayload, /) -> Guild:
        return Guild(data=guild, state=self)

    @property
    def emojis(self) -> Sequence[Emoji]:
        return utils.SequenceProxy(self._emojis.values())

    @property
    def private_channels(self) -> Sequence[PrivateChannel]:
        return utils.SequenceProxy(self._private_channels.values())

    def _get_private_channel(
        self, channel_id: Optional[int]
    ) -> Optional[PrivateChannel]:
        # The keys of self._private_channels are ints
        return self._private_channels.get(channel_id)  # type: ignore

    def _get_private_channel_by_user(
        self, user_id: Optional[int]
    ) -> Optional[DMChannel]:
        # The keys of self._private_channels are ints
        return self._private_channels_by_user.get(user_id)  # type: ignore

    def _add_private_channel(self, channel: PrivateChannel) -> None:
        channel_id = channel.id
        self._private_channels[channel_id] = channel

        if isinstance(channel, DMChannel) and channel.recipient:
            self._private_channels_by_user[channel.recipient.id] = channel

    def add_dm_channel(self, data: DMChannelPayload) -> DMChannel:
        # self.user is *always* cached when this is called
        channel = DMChannel(me=self.user, state=self, data=data)  # type: ignore
        self._add_private_channel(channel)
        return channel

    def _remove_private_channel(self, channel: PrivateChannel) -> None:
        self._private_channels.pop(channel.id, None)
        if isinstance(channel, DMChannel):
            recipient = channel.recipient
            if recipient is not None:
                self._private_channels_by_user.pop(recipient.id, None)

    def _get_message(self, msg_id: Optional[int]) -> Optional[Message]:
        return (
            utils.find(lambda m: m.id == msg_id, reversed(self._messages))
            if self._messages
            else utils.find(
                lambda m: m.id == msg_id, reversed(self._call_message_cache.values())
            )
        )

    def _add_guild_from_data(self, data: GuildPayload) -> Guild:
        guild = self.create_guild(data)
        self._add_guild(guild)
        return guild

    def _guild_needs_chunking(self, guild: Guild) -> bool:
        return (
            self._chunk_guilds
            and not guild.chunked
            and not guild._offline_members_hidden
            and not guild.unavailable
        )

    def _get_guild_channel(
        self, data: PartialMessagePayload, guild_id: Optional[int] = None
    ) -> Tuple[Union[Channel], Optional[Guild]]:
        channel_id = int(data["channel_id"])
        try:
            guild_id = guild_id or int(data["guild_id"])
            guild = self._get_guild(guild_id)
        except KeyError:
            channel = self.get_channel(channel_id)
            guild = None
        else:
            channel = guild and guild._resolve_channel(channel_id)

        return (
            channel or PartialMessageable(state=self, guild_id=guild_id, id=channel_id),
            guild,
        )

    def request_guild(
        self,
        guild_id: int,
        typing: bool = True,
        activities: bool = True,
        threads: bool = True,
    ) -> Coroutine:
        return self.ws.request_lazy_guild(
            guild_id, typing=typing, activities=activities, threads=threads
        )

    def chunker(
        self,
        guild_id: int,
        query: Optional[str] = "",
        limit: int = 0,
        presences: bool = True,
        *,
        user_ids: Optional[List[Snowflake]] = None,
        nonce: Optional[str] = None,
    ):
        return self.ws.request_chunks(
            [guild_id],
            query=query,
            limit=limit,
            presences=presences,
            user_ids=user_ids,
            nonce=nonce,
        )

    async def _delay_ready(self) -> None:
        try:
            states = []
            for guild in self._guilds.values():
                if self._request_guilds:
                    await self.request_guild(guild.id)

            for guild, future in states:
                try:
                    await asyncio.wait_for(future, timeout=10)
                except asyncio.TimeoutError:
                    _log.warning(
                        "Timed out waiting for member list subscriptions for"
                        " guild_id %s.",
                        guild.id,
                    )
                except (ClientException, InvalidData):
                    pass
        except asyncio.CancelledError:
            pass
        else:
            # Dispatch the event
            self.call_handlers("ready")
            self.dispatch("ready")
        finally:
            self._ready_task = None

    def parse_ready(self, data: gw.ReadyEvent) -> None:
        if self._ready_task is not None:
            self._ready_task.cancel()
        self.clear()
        self._ready_data = data

        # Clear the ACK token
        self.http.ack_token = None

        # Self parsing
        self.user = user = ClientUser(state=self, data=data["user"])
        self._users[user.id] = user  # type: ignore

        # Read state parsing
        read_states = data.get("read_state", {})
        for read_state in read_states["entries"]:
            item = ReadState(state=self, data=read_state)
            self.store_read_state(item)
        self.read_state_version = read_states.get("version", 0)

        # Extras
        self.analytics_token = data.get("analytics_token")
        self.preferred_rtc_regions = data.get("geo_ordered_rtc_regions", ["us-central"])
        self.settings = UserSettings(self, data.get("user_settings_proto", ""))
        self.country_code = data.get("country_code", "US")
        self.api_code_version = data.get("api_code_version", 1)
        self.session_type = data.get("session_type", "normal")
        self.auth_session_id = data.get("auth_session_id_hash")

        if "sessions" in data:
            self.parse_sessions_replace(data["sessions"], from_ready=True)

        if "auth_token" in data:
            self.http._token(data["auth_token"])

        # Before parsing the rest, we wait for READY_SUPPLEMENTAL
        # This has voice state objects, as well as an initial member cache

    def parse_ready_supplemental(self, extra_data: gw.ReadySupplementalEvent) -> None:
        data = self._ready_data

        # Temp user parsing
        user = self.user
        temp_users: Dict[int, PartialUserPayload] = {
            int(data["user"]["id"]): data["user"]
        }
        for u in data.get("users", []):
            u_id = int(u["id"])
            temp_users[u_id] = u

        # Discord bad
        for guild_data, guild_extra, merged_members, merged_me, merged_presences in zip(
            data.get("guilds", []),
            extra_data.get("guilds", []),
            extra_data.get("merged_members", []),
            data.get("merged_members", []),
            extra_data["merged_presences"].get("guilds", []),
        ):
            for presence in merged_presences:
                presence["user"] = {"id": presence["user_id"]}  # type: ignore

            if "properties" in guild_data:
                guild_data.update(guild_data.pop("properties"))  # type: ignore

            members = guild_data.setdefault("members", [])
            members.extend(merged_me)
            members.extend(merged_members)
            presences = guild_data.setdefault("presences", [])
            presences.extend(merged_presences)

            for member in members:
                if "user" not in member:
                    member["user"] = temp_users.get(int(member.pop("user_id")))

        # Guild parsing
        for guild_data in data.get("guilds", []):
            self._add_guild_from_data(guild_data)

        # Relationship parsing
        for relationship in data.get("relationships", []):
            try:
                r_id = int(relationship["id"])
            except KeyError:
                continue
            else:
                if "user" not in relationship:
                    relationship["user"] = temp_users[int(relationship.pop("user_id"))]

        # Relationship presence parsing
        for presence in extra_data["merged_presences"].get("friends", []):
            user_id = int(presence.pop("user_id"))  # type: ignore
            self.store_presence(user_id, self.create_presence(presence))

        # Private channel parsing
        for pm in data.get("private_channels", []) + extra_data.get(
            "lazy_private_channels", []
        ):
            factory, _ = _private_channel_factory(pm["type"])
            if "recipients" not in pm:
                pm["recipients"] = [temp_users[int(u_id)] for u_id in pm.pop("recipient_ids")]  # type: ignore
            self._add_private_channel(factory(me=user, data=pm, state=self))  # type: ignore

        # Disloses
        self.disclose = data.get("disclose", [])

        # We're done
        del self._ready_data
        self.call_handlers("connect")
        self.dispatch("connect")
        self._ready_task = asyncio.create_task(self._delay_ready())

    def parse_resumed(self, data: gw.ResumedEvent) -> None:
        self.dispatch("resumed")

    def parse_passive_update_v1(self, data: gw.PassiveUpdateEvent) -> None:
        # PASSIVE_UPDATE_V1 is sent for large guilds you are not subscribed to
        # in order to keep their read and voice states up-to-date; it replaces CHANNEL_UNREADS_UPDATE
        guild = self._get_guild(int(data["guild_id"]))
        if not guild:
            _log.debug(
                "PASSIVE_UPDATE_V1 referencing an unknown guild ID: %s. Discarding.",
                data["guild_id"],
            )
            return

        for channel_data in data.get("channels", []):
            channel = guild.get_channel(int(channel_data["id"]))
            if not channel:
                continue
            channel.last_message_id = utils._get_as_snowflake(channel_data, "last_message_id")  # type: ignore

    def parse_message_create(self, data: gw.MessageCreateEvent) -> None:
        channel, _ = self._get_guild_channel(data)

        # channel will be the correct type here
        message = Message(channel=channel, data=data, state=self)  # type: ignore
        self.dispatch("message", message)
        if self._messages is not None:
            self._messages.append(message)
        if channel:
            channel.last_message_id = message.id  # type: ignore

    def parse_message_update(self, data: gw.MessageUpdateEvent) -> None:
        raw = RawMessageUpdateEvent(data)
        message = self._get_message(raw.message_id)
        if message is not None:
            older_message = copy.copy(message)
            raw.cached_message = older_message
            self.dispatch("raw_message_edit", raw)
            message._update(data)
            # Coerce the `after` parameter to take the new updated Member
            # ref: #5999
            self.dispatch("message_edit", older_message, message)
        else:
            self.dispatch("raw_message_edit", raw)

    def parse_message_ack(self, data: gw.MessageAckEvent) -> None:
        self.read_state_version = data.get("version", self.read_state_version)
        channel_id = int(data["channel_id"])
        channel = self.get_channel(channel_id)
        if channel is None:
            _log.debug(
                "MESSAGE_ACK referencing an unknown channel ID: %s. Discarding.",
                channel_id,
            )
            return

        raw = RawMessageAckEvent(data)
        message_id = int(data["message_id"])
        message = self._get_message(message_id)
        raw.cached_message = message

        read_state = self.get_read_state(channel_id)
        read_state.last_acked_id = message_id
        if "flags" in data and data["flags"] is not None:
            read_state._flags = data["flags"]

        self.dispatch("raw_message_ack", raw)
        if message is not None:
            self.dispatch("message_ack", message, raw.manual)

    def parse_presences_replace(self, data: List[gw.PartialPresenceUpdate]) -> None:
        for presence in data:
            self.parse_presence_update(presence)

    def parse_user_update(self, data: gw.UserUpdateEvent) -> None:
        # Clear the ACK toke
        self.http.ack_token = None
        if self.user:
            self.user._full_update(data)

    def parse_user_settings_proto_update(self, data: gw.ProtoSettingsEvent):
        type = UserSettingsType(data["settings"]["type"])
        if type == UserSettingsType.preloaded_user_settings:
            settings = self.settings
            if settings:
                old_settings = UserSettings._copy(settings)
                settings._update(
                    data["settings"]["proto"], partial=data.get("partial", False)
                )
                self.dispatch("settings_update", old_settings, settings)
                self.dispatch("internal_settings_update", old_settings, settings)
        elif type == UserSettingsType.frecency_user_settings: ...
        elif type == UserSettingsType.test_settings:
            _log.debug(
                "Received test settings proto update. Data: %s",
                data["settings"]["proto"],
            )
        else:
            _log.warning("Unknown user settings proto type: %s", type.value)

    def parse_user_non_channel_ack(self, data: gw.NonChannelAckEvent) -> None:
        self.read_state_version = data.get("version", self.read_state_version)

        raw = RawUserFeatureAckEvent(data)
        read_state = self.get_read_state(self.self_id, raw.type)  # type: ignore
        read_state.last_acked_id = int(data["entity_id"])
        self.dispatch("user_feature_ack", raw)

    def parse_oauth2_token_revoke(self, data: gw.OAuth2TokenRevokeEvent) -> None:
        if "access_token" not in data:
            _log.warning(
                "OAUTH2_TOKEN_REVOKE payload has invalid data: %s. Discarding.",
                list(data.keys()),
            )
        self.dispatch("oauth2_token_revoke", data["access_token"])

    def parse_auth_session_change(self, data: gw.AuthSessionChangeEvent) -> None:
        self.auth_session_id = auth_session_id = data["auth_session_id_hash"]
        self.dispatch("auth_session_change", auth_session_id)

    def parse_sessions_replace(
        self, payload: gw.SessionsReplaceEvent, *, from_ready: bool = False
    ) -> None:
        data = {s["session_id"]: s for s in payload}

        for session_id, session in data.items():
            existing = self._sessions.get(session_id)
            if existing is not None:
                old = copy.copy(existing)
                existing._update(session)
                if not from_ready and (
                    old.status != existing.status
                    or old.active != existing.active
                    or old.activities != existing.activities
                ):
                    self.dispatch("session_update", old, existing)
            else:
                existing = Session(state=self, data=session)
                self._sessions[session_id] = existing
                if not from_ready:
                    self.dispatch("session_create", existing)

        old_all = None
        if not from_ready:
            removed_sessions = [s for s in self._sessions if s not in data]
            for session_id in removed_sessions:
                if session_id == "all":
                    old_all = self._sessions.pop("all")
                else:
                    session = self._sessions.pop(session_id)
                    self.dispatch("session_delete", session)

        if "all" not in self._sessions:
            # The "all" session does not always exist...
            # This usually happens if there is only a single session (us)
            # In the case it is "removed", we try to update the old one
            # Else, we create a new one with fake data
            if len(data) > 1:
                # We have more than one session, this should not happen
                fake = data[self.session_id]  # type: ignore
            else:
                fake = list(data.values())[0]
            if old_all is not None:
                old = copy.copy(old_all)
                old_all._update(fake)
                if (
                    old.status != old_all.status
                    or old.active != old_all.active
                    or old.activities != old_all.activities
                ):
                    self.dispatch("session_update", old, old_all)
            else:
                old_all = Session._fake_all(state=self, data=fake)
            self._sessions["all"] = old_all

    def parse_guild_application_command_index_update(
        self, data: gw.GuildApplicationCommandIndexUpdateEvent
    ) -> None:
        guild = self._get_guild(int(data["guild_id"]))
        if guild is None:
            _log.debug(
                "GUILD_APPLICATION_COMMAND_INDEX_UPDATE referencing an unknown"
                " guild ID: %s. Discarding.",
                data["guild_id"],
            )
            return

        counts = data["application_command_counts"]
        old_counts = guild.application_command_counts or ApplicationCommandCounts(
            0, 0, 0
        )
        guild.application_command_counts = new_counts = ApplicationCommandCounts(
            counts.get(1, 0), counts.get(2, 0), counts.get(3, 0)
        )
        self.dispatch(
            "application_command_counts_update", guild, old_counts, new_counts
        )

    def parse_interaction_create(self, data: gw.InteractionEvent) -> None:
        if "nonce" not in data:  # Sometimes interactions seem to be missing the nonce
            return

        type, name, channel = self._interaction_cache.pop(
            data["nonce"], (0, None, None)
        )
        i = Interaction._from_self(channel, type=type, user=self.user, name=name, **data)  # type: ignore # self.user is always present here
        self._interactions[i.id] = i
        self.dispatch("interaction", i)

    def parse_interaction_success(self, data: gw.InteractionEvent) -> None:
        id = int(data["id"])
        i = self._interactions.get(id, None)
        if i is None:
            _log.warning(
                "INTERACTION_SUCCESS referencing an unknown interaction ID: %s."
                " Discarding.",
                id,
            )
            return

        i.successful = True
        self.dispatch("interaction_finish", i)

    def parse_interaction_failed(self, data: gw.InteractionEvent) -> None:
        id = int(data["id"])
        i = self._interactions.pop(id, None)
        if i is None:
            _log.warning(
                "INTERACTION_FAILED referencing an unknown interaction ID: %s."
                " Discarding.",
                id,
            )
            return

        i.successful = False
        self.dispatch("interaction_finish", i)

    def parse_interaction_modal_create(
        self, data: gw.InteractionModalCreateEvent
    ) -> None:
        id = int(data["id"])
        interaction = self._interactions.pop(id, None)
        if interaction is not None:
            modal = Modal(data=data, interaction=interaction)
            interaction.modal = modal
            self.dispatch("modal", modal)

    # Silence "unknown event" warnings for events parsed elsewhere
    parse_nothing = lambda *_: None
    parse_thread_member_list_update = (
        parse_nothing  # Grabbed directly in Thread.fetch_members
    )
    # parse_guild_application_commands_update = parse_nothing  # Grabbed directly in command iterators

    def get_channel(self, id: Optional[int]) -> Optional[Union[Channel]]:
        if id is None:
            return None

        pm = self._get_private_channel(id)
        if pm is not None:
            return pm

        for guild in self.guilds:
            channel = guild._resolve_channel(id)
            if channel is not None:
                return channel

    def _get_or_create_partial_messageable(
        self, id: Optional[int]
    ) -> Optional[Union[Channel]]:
        if id is None:
            return None

        return self.get_channel(id) or PartialMessageable(state=self, id=id)

    def create_message(
        self,
        *,
        channel: MessageableChannel,
        data: MessagePayload,
        search_result: Optional[MessageSearchResultPayload] = None,
    ) -> Message:
        return Message(
            state=self, channel=channel, data=data, search_result=search_result
        )

    def _update_message_references(self) -> None:
        # self._messages won't be None when this is called
        for msg in self._messages:  # type: ignore
            if not msg.guild:
                continue

            new_guild = self._get_guild(msg.guild.id)
            if new_guild is not None and new_guild is not msg.guild:
                channel_id = msg.channel.id
                channel = new_guild._resolve_channel(channel_id) or PartialMessageable(
                    state=self, id=channel_id, guild_id=new_guild.id
                )
                msg._rebind_cached_references(new_guild, channel)

    def create_integration_application(
        self, data: IntegrationApplicationPayload
    ) -> IntegrationApplication:
        return IntegrationApplication(state=self, data=data)

    @property
    def all_session(self) -> Optional[Session]:
        return self._sessions.get("all")

    @property
    def current_session(self) -> Optional[Session]:
        return self._sessions.get(self.session_id)  # type: ignore

    @utils.cached_property
    def client_presence(self) -> FakeClientPresence:
        return FakeClientPresence(self)

    def create_presence(self, data: gw.BasePresenceUpdate) -> Presence:
        return Presence(data, self)

    def create_offline_presence(self) -> Presence:
        return Presence._offline()

    def get_presence(
        self, user_id: int, guild_id: Optional[int] = None
    ) -> Optional[Presence]:
        if user_id == self.self_id:
            # Our own presence is unified
            return self.client_presence

        if guild_id is not None:
            guild = self._guild_presences.get(guild_id)
            if guild is not None:
                return guild.get(user_id)
            return
        return self._presences.get(user_id)

    def remove_presence(self, user_id: int, guild_id: Optional[int] = None) -> None:
        if guild_id is not None:
            guild = self._guild_presences.get(guild_id)
            if guild is not None:
                guild.pop(user_id, None)
        else:
            self._presences.pop(user_id, None)

    def store_presence(
        self, user_id: int, presence: Presence, guild_id: Optional[int] = None
    ) -> Presence:
        if (
            presence.client_status.status == Status.offline.value
            and not presence.activities
        ):
            # We don't store empty presences
            self.remove_presence(user_id, guild_id)
            return presence

        if user_id == self.self_id:
            # We don't store our own presence
            return presence

        if guild_id is not None:
            guild = self._guild_presences.get(guild_id)
            if guild is None:
                guild = self._guild_presences[guild_id] = {}
            guild[user_id] = presence
        else:
            self._presences[user_id] = presence
        return presence

    @overload
    def get_read_state(
        self, id: int, type: ReadStateType = ..., *, if_exists: Literal[False] = ...
    ) -> ReadState: ...

    @overload
    def get_read_state(
        self, id: int, type: ReadStateType = ..., *, if_exists: Literal[True]
    ) -> Optional[ReadState]: ...

    def get_read_state(
        self,
        id: int,
        type: ReadStateType = ReadStateType.channel,
        *,
        if_exists: bool = False,
    ) -> Optional[ReadState]:
        try:
            return self._read_states[type.value][id]
        except KeyError:
            if not if_exists:
                # Create and store a default read state
                state = ReadState.default(id, type, state=self)
                self.store_read_state(state)
                return state

    def remove_read_state(self, read_state: ReadState) -> None:
        try:
            group = self._read_states[read_state.type.value]
        except KeyError:
            return
        group.pop(read_state.id, None)

    def store_read_state(self, read_state: ReadState):
        try:
            group = self._read_states[read_state.type.value]
        except KeyError:
            group = self._read_states[read_state.type.value] = {}
        group[read_state.id] = read_state
