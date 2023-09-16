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

from datetime import datetime
from typing import (
    Dict,
    List,
    NamedTuple,
    Sequence,
    Optional,
    TYPE_CHECKING,
    Tuple,
    Union,
)

from . import utils
from .asset import Asset
from .flags import SystemChannelFlags
from .mixins import Hashable

if TYPE_CHECKING:
    from .types.guild import (
        BaseGuild as BaseGuildPayload,
        Guild as GuildPayload,
        UserGuild as UserGuildPayload,
    )
    from .channel import (
        TextChannel,
        CategoryChannel,
    )
    from .state import ConnectionState
    from .types.oauth2 import OAuth2Guild as OAuth2GuildPayload

    NonCategoryChannel = Union[TextChannel]
    GuildChannel = Union[NonCategoryChannel, CategoryChannel]
    ByCategoryItem = Tuple[Optional[CategoryChannel], List[NonCategoryChannel]]

MISSING = utils.MISSING

__all__ = (
    "Guild",
    "UserGuild",
    "ApplicationCommandCounts",
)


class ApplicationCommandCounts(NamedTuple):
    chat_input: int
    user: int
    message: int


class _GuildLimit(NamedTuple):
    emoji: int


class UserGuild(Hashable):
    """Represents a partial joined guild.

    .. container:: operations

        .. describe:: x == y

            Checks if two guilds are equal.

        .. describe:: x != y

            Checks if two guilds are not equal.

        .. describe:: hash(x)

            Returns the guild's hash.

        .. describe:: str(x)

            Returns the guild's name.

    .. versionadded:: 2.0

    Attributes
    ----------
    id: :class:`int`
        The guild's ID.
    name: :class:`str`
        The guild name.
    features: List[:class:`str`]
        A list of features that the guild has. The features that a guild can have are
        subject to arbitrary change by Discord. Incomplete when retrieved from :attr:`OAuth2Authorization.guilds`.
    owner: :class:`bool`
        Whether the current user is the owner of the guild. Inaccurate when retrieved from :attr:`OAuth2Authorization.guilds`.
    approximate_member_count: Optional[:class:`int`]
        The approximate number of members in the guild. Only available using
        using :meth:`Client.fetch_guilds` with ``with_counts=True``.
    approximate_presence_count: Optional[:class:`int`]
        The approximate number of members currently active in the guild.
        Offline members are excluded. Only available using
        :meth:`Client.fetch_guilds` with ``with_counts=True``.
    """

    __slots__ = (
        "id",
        "name",
        "_icon",
        "owner",
        "_permissions",
        "mfa_level",
        "features",
        "approximate_member_count",
        "approximate_presence_count",
        "_state",
    )

    def __init__(
        self,
        *,
        state: ConnectionState,
        data: Union[UserGuildPayload, OAuth2GuildPayload],
    ):
        self._state: ConnectionState = state
        self.id: int = int(data["id"])
        self.name: str = data["name"]
        self._icon: Optional[str] = data.get("icon")
        self.owner: bool = data.get("owner", False)
        self._permissions: int = int(data.get("permissions", 0))
        self.features: List[str] = data.get("features", [])
        self.approximate_member_count: Optional[int] = data.get(
            "approximate_member_count"
        )
        self.approximate_presence_count: Optional[int] = data.get(
            "approximate_presence_count"
        )

    def __str__(self) -> str:
        return self.name or ""

    def __repr__(self) -> str:
        return f"<UserGuild id={self.id} name={self.name!r}>"

    @property
    def icon(self) -> Optional[Asset]:
        """Optional[:class:`Asset`]: Returns the guild's icon asset, if available."""
        if self._icon is None:
            return None
        return Asset._from_guild_icon(self._state, self.id, self._icon)


class Guild(Hashable):
    """Represents a Discord guild.

    This is referred to as a "server" in the official Discord UI.

    .. container:: operations

        .. describe:: x == y

            Checks if two guilds are equal.

        .. describe:: x != y

            Checks if two guilds are not equal.

        .. describe:: hash(x)

            Returns the guild's hash.

        .. describe:: str(x)

            Returns the guild's name.

    Attributes
    ----------
    name: :class:`str`
        The guild name.
    id: :class:`int`
        The guild's ID.
    unavailable: :class:`bool`
        Indicates if the guild is unavailable. If this is ``True`` then the
        reliability of other attributes outside of :attr:`Guild.id` is slim and they might
        all be ``None``. It is best to not do anything with the guild if it is unavailable.

        Check the :func:`on_guild_unavailable` and :func:`on_guild_available` events.
    application_command_counts: Optional[:class:`ApplicationCommandCounts`]
        A namedtuple representing the number of application commands in the guild, separated by type.

        .. versionadded:: 2.0
    """

    __slots__ = (
        "afk_timeout",
        "name",
        "id",
        "unavailable",
        "owner_id",
        "emojis",
        "features",
        "verification_level",
        "explicit_content_filter",
        "default_notifications",
        "description",
        "max_presences",
        "max_members",
        "max_video_channel_users",
        "preferred_locale",
        "mfa_level",
        "vanity_url_code",
        "application_id",
        "widget_enabled",
        "_widget_channel_id",
        "_members",
        "_channels",
        "_icon",
        "_banner",
        "_state",
        "_roles",
        "_member_count",
        "_large",
        "_splash",
        "_afk_channel_id",
        "_system_channel_id",
        "_system_channel_flags",
        "_discovery_splash",
        "_rules_channel_id",
        "_public_updates_channel_id",
        "_stage_instances",
        "_scheduled_events",
        "_threads",
        "approximate_member_count",
        "approximate_presence_count",
        "_presence_count",
        "_true_online_count",
        "_chunked",
        "_member_list",
        "keywords",
        "primary_category_id",
        "application_command_counts",
        "hub_type",
        "_joined_at",
        "_cs_joined",
    )

    def __init__(
        self, *, data: Union[BaseGuildPayload, GuildPayload], state: ConnectionState
    ) -> None:
        self._chunked = False
        self._cs_joined: Optional[bool] = None
        self._channels: Dict[int, GuildChannel] = {}
        self._state: ConnectionState = state
        self.application_command_counts: Optional[ApplicationCommandCounts] = None
        self._member_count: Optional[int] = None
        self._presence_count: Optional[int] = None
        self._large: Optional[bool] = None
        self._from_data(data)

    def __str__(self) -> str:
        return self.name or ""

    def __repr__(self) -> str:
        attrs = (
            ("id", self.id),
            ("name", self.name),
            ("chunked", self.chunked),
            ("member_count", self.member_count),
        )
        inner = " ".join("%s=%r" % t for t in attrs)
        return f"<Guild {inner}>"

    @classmethod
    def _create_unavailable(cls, *, state: ConnectionState, guild_id: int) -> Guild:
        return cls(state=state, data={"id": guild_id, "unavailable": True})  # type: ignore

    def _from_data(self, guild: Union[BaseGuildPayload, GuildPayload]) -> None:
        try:
            self._member_count: Optional[int] = guild["member_count"]  # type: ignore # Handled below
        except KeyError:
            pass

        self.id: int = int(guild["id"])
        self.name: str = guild.get("name", "")
        self.unavailable: bool = guild.get("unavailable", False)
        if self.unavailable:
            self._member_count = 0

        state = self._state  # Speed up attribute access

    @property
    def channels(self) -> Sequence[GuildChannel]:
        """Sequence[:class:`abc.GuildChannel`]: A list of channels that belongs to this guild."""
        return utils.SequenceProxy(self._channels.values())

    @property
    def large(self) -> bool:
        """:class:`bool`: Indicates if the guild is a 'large' guild.

        A large guild is defined as having more than ``large_threshold`` count
        members, which for this library is set to the maximum of 250.
        """
        if self._large is None:
            if self._member_count is not None:
                return self._member_count >= 250
            return len(self._members) >= 250
        return self._large

    @property
    def _offline_members_hidden(self) -> bool:
        return (self._member_count or 0) > 1000

    @property
    def joined_at(self) -> Optional[datetime]:
        """:class:`datetime.datetime`: Returns when you joined the guild.

        .. versionadded:: 2.0
        """
        return utils.parse_time(self._joined_at)

    @property
    def text_channels(self) -> List[TextChannel]:
        """List[:class:`TextChannel`]: A list of text channels that belongs to this guild.

        This is sorted by the position and are in UI order from top to bottom.
        """
        r = [ch for ch in self._channels.values() if isinstance(ch, TextChannel)]
        r.sort(key=lambda c: (c.position, c.id))
        return r

    @property
    def categories(self) -> List[CategoryChannel]:
        """List[:class:`CategoryChannel`]: A list of categories that belongs to this guild.

        This is sorted by the position and are in UI order from top to bottom.
        """
        r = [ch for ch in self._channels.values() if isinstance(ch, CategoryChannel)]
        r.sort(key=lambda c: (c.position, c.id))
        return r

    def by_category(self) -> List[ByCategoryItem]:
        """Returns every :class:`CategoryChannel` and their associated channels.

        These channels and categories are sorted in the official Discord UI order.

        If the channels do not have a category, then the first element of the tuple is
        ``None``.

        Returns
        --------
        List[Tuple[Optional[:class:`CategoryChannel`], List[:class:`abc.GuildChannel`]]]:
            The categories and their associated channels.
        """
        grouped: Dict[Optional[int], List[NonCategoryChannel]] = {}
        for channel in self._channels.values():
            if isinstance(channel, CategoryChannel):
                grouped.setdefault(channel.id, [])
                continue

            try:
                grouped[channel.category_id].append(channel)
            except KeyError:
                grouped[channel.category_id] = [channel]

        def key(t: ByCategoryItem) -> Tuple[Tuple[int, int], List[NonCategoryChannel]]:
            k, v = t
            return ((k.position, k.id) if k else (-1, -1), v)

        _get = self._channels.get
        as_list: List[ByCategoryItem] = [(_get(k), v) for k, v in grouped.items()]  # type: ignore
        as_list.sort(key=key)
        for _, channels in as_list:
            channels.sort(key=lambda c: (c._sorting_bucket, c.position, c.id))
        return as_list

    def _resolve_channel(self, id: Optional[int], /) -> Optional[Union[GuildChannel]]:
        if id is None:
            return

        return self._channels.get(id)

    def get_channel_or_thread(
        self, channel_id: int, /
    ) -> Optional[Union[GuildChannel]]:
        """Returns a channel or thread with the given ID.

        .. versionadded:: 2.0

        Parameters
        -----------
        channel_id: :class:`int`
            The ID to search for.

        Returns
        --------
        Optional[Union[:class:`Thread`, :class:`.abc.GuildChannel`]]
            The returned channel, thread, or ``None`` if not found.
        """
        return self._channels.get(channel_id)

    def get_channel(self, channel_id: int, /) -> Optional[GuildChannel]:
        """Returns a channel with the given ID.

        .. note::

            This does *not* search for threads.

        .. versionchanged:: 2.0

            ``channel_id`` parameter is now positional-only.

        Parameters
        -----------
        channel_id: :class:`int`
            The ID to search for.

        Returns
        --------
        Optional[:class:`.abc.GuildChannel`]
            The returned channel or ``None`` if not found.
        """
        return self._channels.get(channel_id)

    @property
    def system_channel(self) -> Optional[TextChannel]:
        """Optional[:class:`TextChannel`]: Returns the guild's channel used for system messages.

        If no channel is set, then this returns ``None``.
        """
        channel_id = self._system_channel_id
        return channel_id and self._channels.get(channel_id)  # type: ignore

    @property
    def system_channel_flags(self) -> SystemChannelFlags:
        """:class:`SystemChannelFlags`: Returns the guild's system channel settings."""
        return SystemChannelFlags._from_value(self._system_channel_flags)

    @property
    def rules_channel(self) -> Optional[TextChannel]:
        """Optional[:class:`TextChannel`]: Return's the guild's channel used for the rules.
        The guild must be a Community guild.

        If no channel is set, then this returns ``None``.

        .. versionadded:: 1.3
        """
        channel_id = self._rules_channel_id
        return channel_id and self._channels.get(channel_id)  # type: ignore

    @property
    def public_updates_channel(self) -> Optional[TextChannel]:
        """Optional[:class:`TextChannel`]: Return's the guild's channel where admins and
        moderators of the guilds receive notices from Discord. The guild must be a
        Community guild.

        If no channel is set, then this returns ``None``.

        .. versionadded:: 1.4
        """
        channel_id = self._public_updates_channel_id
        return channel_id and self._channels.get(channel_id)  # type: ignore

    @property
    def icon(self) -> Optional[Asset]:
        """Optional[:class:`Asset`]: Returns the guild's icon asset, if available."""
        if self._icon is None:
            return None
        return Asset._from_guild_icon(self._state, self.id, self._icon)

    @property
    def banner(self) -> Optional[Asset]:
        """Optional[:class:`Asset`]: Returns the guild's banner asset, if available."""
        if self._banner is None:
            return None
        return Asset._from_guild_image(
            self._state, self.id, self._banner, path="banners"
        )

    @property
    def splash(self) -> Optional[Asset]:
        """Optional[:class:`Asset`]: Returns the guild's invite splash asset, if available."""
        if self._splash is None:
            return None
        return Asset._from_guild_image(
            self._state, self.id, self._splash, path="splashes"
        )

    @property
    def discovery_splash(self) -> Optional[Asset]:
        """Optional[:class:`Asset`]: Returns the guild's discovery splash asset, if available."""
        if self._discovery_splash is None:
            return None
        return Asset._from_guild_image(
            self._state, self.id, self._discovery_splash, path="discovery-splashes"
        )

    @property
    def member_count(self) -> Optional[int]:
        """Optional[:class:`int`]: Returns the member count if available.

        .. warning::

            Due to a Discord limitation, this may not always be up-to-date and accurate.
        """
        return (
            self._member_count
            if self._member_count is not None
            else self.approximate_member_count
        )

    @property
    def online_count(self) -> Optional[int]:
        """Optional[:class:`int`]: Returns the online member count.

        .. versionadded:: 1.9

        .. warning::

            Due to a Discord limitation, this may not always be up-to-date and accurate.
        """
        return self._presence_count

    @property
    def chunked(self) -> bool:
        """:class:`bool`: Returns a boolean indicating if the guild is "chunked".

        A chunked guild means that :attr:`member_count` is equal to the
        number of members stored in the internal :attr:`members` cache.

        If this value returns ``False``, then you should request for
        offline members.
        """
        return self._chunked

    @property
    def created_at(self) -> datetime:
        """:class:`datetime.datetime`: Returns the guild's creation time in UTC."""
        return utils.snowflake_time(self.id)

    async def ack(self) -> None:
        """|coro|

        Marks every message in this guild as read.

        Raises
        -------
        HTTPException
            Acking failed.
        """
        return await self._state.http.ack_guild(self.id)
