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

from typing import Generic, List, Literal, Optional, TypedDict, TypeVar
from typing_extensions import NotRequired

from .channel import ChannelType
from .guild import ApplicationCommandCounts, Guild, SupplementalGuild
from .interactions import Modal
from .message import Message
from .read_state import ReadState, ReadStateType
from .snowflake import Snowflake
from .user import (
    Connection,
    PartialConsentSettings,
    PartialUser,
    ProtoSettingsType,
    Relationship,
    User,
    UserGuildSettings,
)

T = TypeVar("T")


class Gateway(TypedDict):
    url: str


class ShardInfo(TypedDict):
    shard_id: int
    shard_count: int


class ResumedEvent(TypedDict):
    _trace: List[str]


class ReadyEvent(ResumedEvent):
    _trace: List[str]
    api_code_version: int
    analytics_token: str
    auth_session_id_hash: str
    auth_token: NotRequired[str]
    connected_accounts: List[Connection]
    consents: PartialConsentSettings
    country_code: str
    friend_suggestion_count: int
    geo_ordered_rtc_regions: List[str]
    guilds: List[Guild]
    read_state: Versioned[ReadState]
    relationships: List[Relationship]
    resume_gateway_url: str
    required_action: NotRequired[str]
    sessions: List[Session]
    session_id: str
    session_type: Literal["normal"]
    shard: NotRequired[ShardInfo]
    user: User
    user_guild_settings: Versioned[UserGuildSettings]
    user_settings_proto: NotRequired[str]
    users: List[PartialUser]
    v: int


class ClientInfo(TypedDict):
    version: int
    os: str
    client: str


class Session(TypedDict):
    session_id: str
    active: NotRequired[bool]
    client_info: ClientInfo


class ReadySupplementalEvent(TypedDict):
    guilds: List[SupplementalGuild]
    disclose: List[str]


class Versioned(TypedDict, Generic[T]):
    entries: List[T]
    version: int
    partial: bool


NoEvent = Literal[None]


MessageCreateEvent = Message


SessionsReplaceEvent = List[Session]


class MessageDeleteEvent(TypedDict):
    id: Snowflake
    channel_id: Snowflake
    guild_id: NotRequired[Snowflake]


class MessageDeleteBulkEvent(TypedDict):
    ids: List[Snowflake]
    channel_id: Snowflake
    guild_id: NotRequired[Snowflake]


class MessageUpdateEvent(Message):
    channel_id: Snowflake


class _ChannelEvent(TypedDict):
    id: Snowflake
    type: ChannelType


ChannelCreateEvent = ChannelUpdateEvent = ChannelDeleteEvent = _ChannelEvent


class MessageAckEvent(TypedDict):
    channel_id: Snowflake
    message_id: Snowflake
    flags: Optional[int]
    last_viewed: Optional[int]
    manual: NotRequired[bool]
    mention_count: NotRequired[int]
    ack_type: NotRequired[ReadStateType]
    version: int


class NonChannelAckEvent(TypedDict):
    entity_id: Snowflake
    resource_id: Snowflake
    ack_type: int
    version: int


class IntegrationDeleteEvent(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    application_id: NotRequired[Snowflake]


class OAuth2TokenRevokeEvent(TypedDict):
    access_token: str


class AuthSessionChangeEvent(TypedDict):
    auth_session_id_hash: str


class RequiredActionEvent(TypedDict):
    required_action: str


class ProtoSettings(TypedDict):
    proto: str
    type: ProtoSettingsType


class ProtoSettingsEvent(TypedDict):
    settings: ProtoSettings
    partial: bool


class PartialUpdateChannel(TypedDict):
    id: Snowflake
    last_message_id: Optional[Snowflake]


class PassiveUpdateEvent(TypedDict):
    guild_id: Snowflake
    channels: List[PartialUpdateChannel]


class GuildApplicationCommandIndexUpdateEvent(TypedDict):
    guild_id: Snowflake
    application_command_counts: ApplicationCommandCounts


class UserNoteUpdateEvent(TypedDict):
    id: Snowflake
    note: str


UserGuildSettingsEvent = UserGuildSettings


class InteractionEvent(TypedDict):
    id: Snowflake
    nonce: NotRequired[Snowflake]


InteractionModalCreateEvent = Modal
