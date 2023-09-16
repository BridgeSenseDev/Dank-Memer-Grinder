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

import datetime
from typing import (
    AsyncIterator,
    List,
    Literal,
    NamedTuple,
    Optional,
    TYPE_CHECKING,
    TypeVar,
    Union,
)

import discord.abc
from . import utils
from .enums import (
    ChannelType,
    EntityType,
    try_enum,
)
from .mixins import Hashable
from .utils import MISSING

__all__ = (
    "TextChannel",
    "CategoryChannel",
    "DMChannel",
    "PartialMessageable",
)

if TYPE_CHECKING:
    from typing_extensions import Self

    from .object import Object
    from .abc import Snowflake
    from .message import Message, PartialMessage
    from .state import ConnectionState
    from .user import BaseUser, ClientUser, User
    from .guild import Guild, GuildChannel as GuildChannelType
    from .read_state import ReadState
    from .types.channel import (
        TextChannel as TextChannelPayload,
        DMChannel as DMChannelPayload,
        CategoryChannel as CategoryChannelPayload,
    )

    OverwriteKeyT = TypeVar("OverwriteKeyT", BaseUser, Object, Union[Object])


class TextChannel(discord.abc.Messageable, discord.abc.GuildChannel, Hashable):
    """Represents a Discord guild text channel.

    .. container:: operations

        .. describe:: x == y

            Checks if two channels are equal.

        .. describe:: x != y

            Checks if two channels are not equal.

        .. describe:: hash(x)

            Returns the channel's hash.

        .. describe:: str(x)

            Returns the channel's name.

    Attributes
    -----------
    name: :class:`str`
        The channel name.
    guild: :class:`Guild`
        The guild the channel belongs to.
    id: :class:`int`
        The channel ID.
    category_id: Optional[:class:`int`]
        The category channel ID this channel belongs to, if applicable.
    topic: Optional[:class:`str`]
        The channel's topic. ``None`` if it doesn't exist.
    position: :class:`int`
        The position in the channel list. This is a number that starts at 0. e.g. the
        top channel is position 0.
    last_message_id: Optional[:class:`int`]
        The last message ID of the message sent to this channel. It may
        *not* point to an existing or valid message.
    slowmode_delay: :class:`int`
        The number of seconds a member must wait between sending messages
        in this channel. A value of ``0`` denotes that it is disabled.
        Bots and users with :attr:`~Permissions.manage_channels` or
        :attr:`~Permissions.manage_messages` bypass slowmode.
    """

    __slots__ = (
        "name",
        "id",
        "guild",
        "topic",
        "_state",
        "category_id",
        "position",
        "slowmode_delay",
        "_overwrites",
        "_type",
        "last_message_id",
    )

    def __init__(
        self,
        *,
        state: ConnectionState,
        guild: Guild,
        data: Union[TextChannelPayload],
    ):
        self._state: ConnectionState = state
        self.id: int = int(data["id"])
        self._type: Literal[0, 5] = data["type"]
        self._update(guild, data)

    def __repr__(self) -> str:
        attrs = [
            ("id", self.id),
            ("name", self.name),
            ("position", self.position),
            ("category_id", self.category_id),
        ]
        joined = " ".join("%s=%r" % t for t in attrs)
        return f"<{self.__class__.__name__} {joined}>"

    def _update(self, guild: Guild, data: Union[TextChannelPayload]) -> None:
        self.guild: Guild = guild
        self.name: str = data["name"]
        self.category_id: Optional[int] = utils._get_as_snowflake(data, "parent_id")
        self.topic: Optional[str] = data.get("topic")
        self.position: int = data["position"]
        # Does this need coercion into `int`? No idea yet.
        self.slowmode_delay: int = data.get("rate_limit_per_user", 0)
        self._type: Literal[0, 5] = data.get("type", self._type)
        self.last_message_id: Optional[int] = utils._get_as_snowflake(
            data, "last_message_id"
        )
        self._fill_overwrites(data)

    async def _get_channel(self) -> Self:
        return self

    @property
    def type(self) -> ChannelType:
        """:class:`ChannelType`: The channel's Discord type."""
        return try_enum(ChannelType, self._type)

    @property
    def _sorting_bucket(self) -> int:
        return ChannelType.text.value

    @property
    def _scheduled_event_entity_type(self) -> Optional[EntityType]:
        return None

    @property
    def read_state(self) -> ReadState:
        """:class:`ReadState`: Returns the read state for this channel.

        .. versionadded:: 2.1
        """
        return self._state.get_read_state(self.id)

    @property
    def last_message(self) -> Optional[Message]:
        """Retrieves the last message from this channel in cache.

        The message might not be valid or point to an existing message.

        .. admonition:: Reliable Fetching
            :class: helpful

            For a slightly more reliable method of fetching the
            last message, consider using either :meth:`history`
            or :meth:`fetch_message` with the :attr:`last_message_id`
            attribute.

        Returns
        ---------
        Optional[:class:`Message`]
            The last message in this channel or ``None`` if not found.
        """
        return (
            self._state._get_message(self.last_message_id)
            if self.last_message_id
            else None
        )

    @property
    def acked_message_id(self) -> int:
        """:class:`int`: The last message ID that the user has acknowledged.
        It may *not* point to an existing or valid message.

        .. versionadded:: 2.1
        """
        return self.read_state.last_acked_id

    @property
    def acked_message(self) -> Optional[Message]:
        """Retrieves the last message that the user has acknowledged in cache.

        The message might not be valid or point to an existing message.

        .. versionadded:: 2.1

        .. admonition:: Reliable Fetching
            :class: helpful

            For a slightly more reliable method of fetching the
            last acknowledged message, consider using either :meth:`history`
            or :meth:`fetch_message` with the :attr:`acked_message_id`
            attribute.

        Returns
        ---------
        Optional[:class:`Message`]
            The last acknowledged message in this channel or ``None`` if not found.
        """
        acked_message_id = self.acked_message_id
        if acked_message_id is None:
            return

        # We need to check if the message is in the same channel
        message = self._state._get_message(acked_message_id)
        if message and message.channel.id == self.id:
            return message

    def get_partial_message(self, message_id: int, /) -> PartialMessage:
        """Creates a :class:`PartialMessage` from the message ID.

        This is useful if you want to work with a message and only have its ID without
        doing an unnecessary API call.

        .. versionadded:: 1.6

        .. versionchanged:: 2.0

            ``message_id`` parameter is now positional-only.

        Parameters
        ------------
        message_id: :class:`int`
            The message ID to create a partial message for.

        Returns
        ---------
        :class:`PartialMessage`
            The partial message.
        """

        from .message import PartialMessage

        return PartialMessage(channel=self, id=message_id)


class CategoryChannel(discord.abc.GuildChannel, Hashable):
    """Represents a Discord channel category.

    These are useful to group channels to logical compartments.

    .. container:: operations

        .. describe:: x == y

            Checks if two channels are equal.

        .. describe:: x != y

            Checks if two channels are not equal.

        .. describe:: hash(x)

            Returns the category's hash.

        .. describe:: str(x)

            Returns the category's name.

    Attributes
    -----------
    name: :class:`str`
        The category name.
    guild: :class:`Guild`
        The guild the category belongs to.
    id: :class:`int`
        The category channel ID.
    position: :class:`int`
        The position in the category list. This is a number that starts at 0. e.g. the
        top category is position 0.
    """

    __slots__ = (
        "name",
        "id",
        "guild",
        "_state",
        "position",
        "_overwrites",
        "category_id",
    )

    def __init__(
        self, *, state: ConnectionState, guild: Guild, data: CategoryChannelPayload
    ):
        self._state: ConnectionState = state
        self.id: int = int(data["id"])
        self._update(guild, data)

    def __repr__(self) -> str:
        return (
            "<CategoryChannel"
            f" id={self.id} name={self.name!r} position={self.position}>"
        )

    def _update(self, guild: Guild, data: CategoryChannelPayload) -> None:
        self.guild: Guild = guild
        self.name: str = data["name"]
        self.category_id: Optional[int] = utils._get_as_snowflake(data, "parent_id")
        self.position: int = data["position"]
        self._fill_overwrites(data)

    @property
    def _sorting_bucket(self) -> int:
        return ChannelType.category.value

    @property
    def _scheduled_event_entity_type(self) -> Optional[EntityType]:
        return None

    @property
    def type(self) -> ChannelType:
        """:class:`ChannelType`: The channel's Discord type."""
        return ChannelType.category

    @property
    def channels(self) -> List[GuildChannelType]:
        """List[:class:`abc.GuildChannel`]: Returns the channels that are under this category.

        These are sorted by the official Discord UI, which places voice channels below the text channels.
        """

        def comparator(channel):
            return (not isinstance(channel, TextChannel), channel.position)

        ret = [c for c in self.guild.channels if c.category_id == self.id]
        ret.sort(key=comparator)
        return ret

    @property
    def text_channels(self) -> List[TextChannel]:
        """List[:class:`TextChannel`]: Returns the text channels that are under this category."""
        ret = [
            c
            for c in self.guild.channels
            if c.category_id == self.id and isinstance(c, TextChannel)
        ]
        ret.sort(key=lambda c: (c.position, c.id))
        return ret


class DMChannel(
    discord.abc.Messageable,
    discord.abc.Connectable,
    discord.abc.PrivateChannel,
    Hashable,
):
    """Represents a Discord direct message channel.

    .. container:: operations

        .. describe:: x == y

            Checks if two channels are equal.

        .. describe:: x != y

            Checks if two channels are not equal.

        .. describe:: hash(x)

            Returns the channel's hash.

        .. describe:: str(x)

            Returns a string representation of the channel

    Attributes
    ----------
    id: :class:`int`
        The direct message channel ID.
    recipient: :class:`User`
        The user you are participating with in the direct message channel.
    me: :class:`ClientUser`
        The user presenting yourself.
    last_message_id: Optional[:class:`int`]
        The last message ID of the message sent to this channel. It may
        *not* point to an existing or valid message.

        .. versionadded:: 2.0
    """

    __slots__ = (
        "id",
        "recipient",
        "me",
        "last_message_id",
        "_message_request",
        "_requested_at",
        "_spam",
        "_state",
        "_accessed",
    )

    def __init__(
        self, *, me: ClientUser, state: ConnectionState, data: DMChannelPayload
    ):
        self._state: ConnectionState = state
        self.recipient: User = state.store_user(data["recipients"][0])
        self.me: ClientUser = me
        self.id: int = int(data["id"])
        self._update(data)
        self._accessed: bool = False

    def _update(self, data: DMChannelPayload) -> None:
        self.last_message_id: Optional[int] = utils._get_as_snowflake(
            data, "last_message_id"
        )
        self._message_request: Optional[bool] = data.get("is_message_request")
        self._requested_at: Optional[datetime.datetime] = utils.parse_time(
            data.get("is_message_request_timestamp")
        )
        self._spam: bool = data.get("is_spam", False)

    async def _get_channel(self) -> Self:
        if not self._accessed:
            self._accessed = True
        return self

    def __str__(self) -> str:
        if self.recipient:
            return f"Direct Message with {self.recipient}"
        return "Direct Message with Unknown User"

    def __repr__(self) -> str:
        return f"<DMChannel id={self.id} recipient={self.recipient!r}>"

    @property
    def type(self) -> ChannelType:
        """:class:`ChannelType`: The channel's Discord type."""
        return ChannelType.private

    @property
    def created_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: Returns the direct message channel's creation time in UTC."""
        return utils.snowflake_time(self.id)

    @property
    def guild(self) -> Optional[Guild]:
        """Optional[:class:`Guild`]: The guild this DM channel belongs to. Always ``None``.

        This is mainly provided for compatibility purposes in duck typing.

        .. versionadded:: 2.0
        """
        return None

    @property
    def jump_url(self) -> str:
        """:class:`str`: Returns a URL that allows the client to jump to the channel.

        .. versionadded:: 2.0
        """
        return f"https://discord.com/channels/@me/{self.id}"

    @property
    def read_state(self) -> ReadState:
        """:class:`ReadState`: Returns the read state for this channel.

        .. versionadded:: 2.1
        """
        return self._state.get_read_state(self.id)

    @property
    def last_message(self) -> Optional[Message]:
        """Retrieves the last message from this channel in cache.

        The message might not be valid or point to an existing message.

        .. admonition:: Reliable Fetching
            :class: helpful

            For a slightly more reliable method of fetching the
            last message, consider using either :meth:`history`
            or :meth:`fetch_message` with the :attr:`last_message_id`
            attribute.

        Returns
        ---------
        Optional[:class:`Message`]
            The last message in this channel or ``None`` if not found.
        """
        return (
            self._state._get_message(self.last_message_id)
            if self.last_message_id
            else None
        )

    @property
    def acked_message_id(self) -> int:
        """:class:`int`: The last message ID that the user has acknowledged.
        It may *not* point to an existing or valid message.

        .. versionadded:: 2.1
        """
        return self.read_state.last_acked_id

    @property
    def acked_message(self) -> Optional[Message]:
        """Retrieves the last message that the user has acknowledged in cache.

        The message might not be valid or point to an existing message.

        .. versionadded:: 2.1

        .. admonition:: Reliable Fetching
            :class: helpful

            For a slightly more reliable method of fetching the
            last acknowledged message, consider using either :meth:`history`
            or :meth:`fetch_message` with the :attr:`acked_message_id`
            attribute.

        Returns
        ---------
        Optional[:class:`Message`]
            The last acknowledged message in this channel or ``None`` if not found.
        """
        acked_message_id = self.acked_message_id
        if acked_message_id is None:
            return

        # We need to check if the message is in the same channel
        message = self._state._get_message(acked_message_id)
        if message and message.channel.id == self.id:
            return message

    def get_partial_message(self, message_id: int, /) -> PartialMessage:
        """Creates a :class:`PartialMessage` from the message ID.

        This is useful if you want to work with a message and only have its ID without
        doing an unnecessary API call.

        .. versionadded:: 1.6

        .. versionchanged:: 2.0

            ``message_id`` parameter is now positional-only.

        Parameters
        ------------
        message_id: :class:`int`
            The message ID to create a partial message for.

        Returns
        ---------
        :class:`PartialMessage`
            The partial message.
        """

        from .message import PartialMessage

        return PartialMessage(channel=self, id=message_id)

    async def close(self):
        """|coro|

        Closes/"deletes" the channel.

        In reality, if you recreate a DM with the same user,
        all your message history will be there.

        Raises
        -------
        HTTPException
            Closing the channel failed.
        """
        await self._state.http.delete_channel(self.id, silent=False)

    async def accept(self) -> DMChannel:
        """|coro|

        Accepts a message request.

        Raises
        -------
        HTTPException
            Accepting the message request failed.
        TypeError
            The channel is not a message request or the request is already accepted.
        """
        data = await self._state.http.accept_message_request(self.id)
        # Of course Discord does not actually include these fields
        data["is_message_request"] = False
        if self._requested_at:
            data["is_message_request_timestamp"] = self._requested_at.isoformat()
        data["is_spam"] = self._spam

        return DMChannel(state=self._state, data=data, me=self.me)

    async def decline(self) -> None:
        """|coro|

        Declines a message request. This closes the channel.

        Raises
        -------
        HTTPException
            Declining the message request failed.
        TypeError
            The channel is not a message request or the request is already accepted.
        """
        await self._state.http.decline_message_request(self.id)


class PartialMessageable(discord.abc.Messageable, Hashable):
    """Represents a partial messageable to aid with working messageable channels when
    only a channel ID is present.

    The only way to construct this class is through :meth:`Client.get_partial_messageable`.

    Note that this class is trimmed down and has no rich attributes.

    .. container:: operations

        .. describe:: x == y

            Checks if two partial messageables are equal.

        .. describe:: x != y

            Checks if two partial messageables are not equal.

        .. describe:: hash(x)

            Returns the partial messageable's hash.

    .. versionadded:: 2.0

    Attributes
    -----------
    id: :class:`int`
        The channel ID associated with this partial messageable.
    type: Optional[:class:`ChannelType`]
        The channel type associated with this partial messageable, if given.
    name: Optional[:class:`str`]
        The channel name associated with this partial messageable, if given.
    guild_id: Optional[:class:`int`]
        The guild ID associated with this partial messageable.
    """

    def __init__(
        self,
        *,
        state: ConnectionState,
        id: int,
        guild_id: Optional[int] = None,
        type: Optional[ChannelType] = None,
        name: Optional[str] = None,
    ):
        self._state: ConnectionState = state
        self.id: int = id
        self.guild_id: Optional[int] = guild_id
        self.type: Optional[ChannelType] = type
        self.name: Optional[str] = name
        self.last_message_id: Optional[int] = None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} type={self.type!r}>"

    async def _get_channel(self) -> PartialMessageable:
        return self

    @property
    def guild(self) -> Optional[Guild]:
        """Optional[:class:`Guild`]: The guild this partial messageable is in."""
        return self._state._get_guild(self.guild_id)

    @property
    def jump_url(self) -> str:
        """:class:`str`: Returns a URL that allows the client to jump to the channel."""
        if self.guild_id is None:
            return f"https://discord.com/channels/@me/{self.id}"
        return f"https://discord.com/channels/{self.guild_id}/{self.id}"

    @property
    def read_state(self) -> ReadState:
        """:class:`ReadState`: Returns the read state for this channel.

        .. versionadded:: 2.1
        """
        return self._state.get_read_state(self.id)

    def get_partial_message(self, message_id: int, /) -> PartialMessage:
        """Creates a :class:`PartialMessage` from the message ID.

        This is useful if you want to work with a message and only have its ID without
        doing an unnecessary API call.

        Parameters
        ------------
        message_id: :class:`int`
            The message ID to create a partial message for.

        Returns
        ---------
        :class:`PartialMessage`
            The partial message.
        """

        from .message import PartialMessage

        return PartialMessage(channel=self, id=message_id)


def _guild_channel_factory(channel_type: int):
    value = try_enum(ChannelType, channel_type)
    if value is ChannelType.text:
        return TextChannel, value
    elif value is ChannelType.category:
        return CategoryChannel, value
    elif value is ChannelType.news:
        return TextChannel, value
    else:
        return None, value


def _private_channel_factory(channel_type: int):
    value = try_enum(ChannelType, channel_type)
    if value is ChannelType.private:
        return DMChannel, value
    else:
        return None, value


def _channel_factory(channel_type: int):
    cls, value = _guild_channel_factory(channel_type)
    if cls is None:
        cls, value = _private_channel_factory(channel_type)
    return cls, value
