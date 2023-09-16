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
    Any,
    AsyncIterator,
    Callable,
    Collection,
    Dict,
    List,
    Literal,
    Optional,
    TYPE_CHECKING,
    Protocol,
    Union,
    overload,
    runtime_checkable,
)

from . import utils
from .commands import (
    ApplicationCommand,
    BaseCommand,
    SlashCommand,
    UserCommand,
    MessageCommand,
    _command_factory,
)
from .enums import ApplicationCommandType, ChannelType
from .object import OLDEST_OBJECT, Object

__all__ = (
    "Snowflake",
    "User",
    "PrivateChannel",
    "GuildChannel",
    "Messageable",
    "Connectable",
    "ApplicationCommand",
)

if TYPE_CHECKING:
    from .user import ClientUser, User
    from .asset import Asset
    from .state import ConnectionState
    from .guild import Guild
    from .message import Message
    from .channel import (
        TextChannel,
        DMChannel,
        PartialMessageable,
    )
    from .types.channel import (
        PermissionOverwrite as PermissionOverwritePayload,
        GuildChannel as GuildChannelPayload,
        OverwriteType,
    )

    MessageableChannel = Union[
        TextChannel,
        DMChannel,
        PartialMessageable,
    ]
    VocalChannel = Union[DMChannel]
    SnowflakeTime = Union["Snowflake", datetime]

MISSING = utils.MISSING


class _Undefined:
    def __repr__(self) -> str:
        return "see-below"


_undefined: Any = _Undefined()


async def _purge_helper(
    channel: Union[TextChannel],
    *,
    limit: Optional[int] = 100,
    check: Callable[[Message], bool] = MISSING,
    before: Optional[SnowflakeTime] = None,
    after: Optional[SnowflakeTime] = None,
    around: Optional[SnowflakeTime] = None,
    oldest_first: Optional[bool] = None,
    reason: Optional[str] = None,
) -> List[Message]:
    if check is MISSING:
        check = lambda m: True

    state = channel._state
    channel_id = channel.id
    iterator = channel.history(
        limit=limit,
        before=before,
        after=after,
        oldest_first=oldest_first,
        around=around,
    )
    ret: List[Message] = []
    count = 0

    async for message in iterator:
        if count == 50:
            to_delete = ret[-50:]
            await state._delete_messages(channel_id, to_delete, reason=reason)
            count = 0
        if not check(message):
            continue

        count += 1
        ret.append(message)

    # Some messages remaining to poll
    to_delete = ret[-count:]
    await state._delete_messages(channel_id, to_delete, reason=reason)
    return ret


@overload
def _handle_commands(
    messageable: Messageable,
    type: Literal[ApplicationCommandType.chat_input],
    *,
    query: Optional[str] = ...,
    limit: Optional[int] = ...,
    command_ids: Optional[Collection[int]] = ...,
    application: Optional[Snowflake] = ...,
    with_applications: bool = ...,
    target: Optional[Snowflake] = ...,
) -> AsyncIterator[SlashCommand]: ...


@overload
def _handle_commands(
    messageable: Messageable,
    type: Literal[ApplicationCommandType.user],
    *,
    query: Optional[str] = ...,
    limit: Optional[int] = ...,
    command_ids: Optional[Collection[int]] = ...,
    application: Optional[Snowflake] = ...,
    with_applications: bool = ...,
    target: Optional[Snowflake] = ...,
) -> AsyncIterator[UserCommand]: ...


@overload
def _handle_commands(
    messageable: Message,
    type: Literal[ApplicationCommandType.message],
    *,
    query: Optional[str] = ...,
    limit: Optional[int] = ...,
    command_ids: Optional[Collection[int]] = ...,
    application: Optional[Snowflake] = ...,
    with_applications: bool = ...,
    target: Optional[Snowflake] = ...,
) -> AsyncIterator[MessageCommand]: ...


async def _handle_commands(
    messageable: Union[Messageable, Message],
    type: ApplicationCommandType,
    *,
    query: Optional[str] = None,
    limit: Optional[int] = None,
    command_ids: Optional[Collection[int]] = None,
    application: Optional[Snowflake] = None,
    with_applications: bool = True,
    target: Optional[Snowflake] = None,
) -> AsyncIterator[BaseCommand]:
    if limit is not None and limit < 0:
        raise ValueError("limit must be greater than or equal to 0")
    if query and command_ids:
        raise TypeError("Cannot specify both query and command_ids")

    state = messageable._state
    endpoint = state.http.search_application_commands
    channel = await messageable._get_channel()
    _, cls = _command_factory(type.value)
    cmd_ids = list(command_ids) if command_ids else None

    application_id = application.id if application else None
    if channel.type == ChannelType.private:
        recipient: User = channel.recipient  # type: ignore
        if not recipient.bot:
            raise TypeError("Cannot fetch commands in a DM with a non-bot user")
        application_id = recipient.id
        target = recipient
    elif channel.type == ChannelType.group:
        return

    prev_cursor = MISSING
    cursor = MISSING
    while True:
        # We keep two cursors because Discord just sends us an infinite loop sometimes
        retrieve = min((25 if not cmd_ids else 0) if limit is None else limit, 25)

        if not application_id and limit is not None:
            limit -= retrieve
        if (
            (not cmd_ids and retrieve < 1)
            or cursor is None
            or (prev_cursor is not MISSING and prev_cursor == cursor)
        ):
            return

        data = await endpoint(
            channel.id,
            type.value,
            limit=retrieve if not application_id else None,
            query=query if not cmd_ids and not application_id else None,
            command_ids=cmd_ids if not application_id and not cursor else None,  # type: ignore
            application_id=application_id,
            include_applications=(
                with_applications if (not application_id or with_applications) else None
            ),
            cursor=cursor,
        )
        prev_cursor = cursor
        cursor = data["cursor"].get("next")
        cmds = data["application_commands"]
        apps = {
            int(app["id"]): state.create_integration_application(app)
            for app in data.get("applications") or []
        }

        for cmd in cmds:
            # Handle faked parameters
            if application_id and query and query.lower() not in cmd["name"]:
                continue
            elif (
                application_id
                and (not cmd_ids or int(cmd["id"]) not in cmd_ids)
                and limit == 0
            ):
                continue

            # We follow Discord behavior
            if (
                application_id
                and limit is not None
                and (not cmd_ids or int(cmd["id"]) not in cmd_ids)
            ):
                limit -= 1

            try:
                cmd_ids.remove(int(cmd["id"])) if cmd_ids else None
            except ValueError:
                pass

            application = apps.get(int(cmd["application_id"]))
            yield cls(
                state=state,
                data=cmd,
                channel=channel,
                target=target,
                application=application,
            )

        cmd_ids = None
        if (
            application_id
            or len(cmds) < min(limit if limit else 25, 25)
            or len(cmds) == limit == 25
        ):
            return


@runtime_checkable
class Snowflake(Protocol):
    """An ABC that details the common operations on a Discord model.

    Almost all :ref:`Discord models <discord_api_models>` meet this
    abstract base class.

    If you want to create a snowflake on your own, consider using
    :class:`.Object`.

    Attributes
    -----------
    id: :class:`int`
        The model's unique ID.
    """

    id: int


@runtime_checkable
class User(Snowflake, Protocol):
    """An ABC that details the common operations on a Discord user.

    The following implement this ABC:

    - :class:`~discord.User`
    - :class:`~discord.ClientUser`
    - :class:`~discord.Member`

    This ABC must also implement :class:`~discord.abc.Snowflake`.

    Attributes
    -----------
    name: :class:`str`
        The user's username.
    discriminator: :class:`str`
        The user's discriminator. This is a legacy concept that is no longer used.
    global_name: Optional[:class:`str`]
        The user's global nickname.
    bot: :class:`bool`
        If the user is a bot account.
    system: :class:`bool`
        If the user is a system account.
    """

    name: str
    discriminator: str
    global_name: Optional[str]
    bot: bool
    system: bool

    @property
    def display_name(self) -> str:
        """:class:`str`: Returns the user's display name."""
        raise NotImplementedError

    @property
    def mention(self) -> str:
        """:class:`str`: Returns a string that allows you to mention the given user."""
        raise NotImplementedError

    @property
    def avatar(self) -> Optional[Asset]:
        """Optional[:class:`~discord.Asset`]: Returns an Asset that represents the user's avatar, if present."""
        raise NotImplementedError

    @property
    def avatar_decoration(self) -> Optional[Asset]:
        """Optional[:class:`~discord.Asset`]: Returns an Asset that represents the user's avatar decoration, if present.

        .. versionadded:: 2.0
        """
        raise NotImplementedError

    @property
    def default_avatar(self) -> Asset:
        """:class:`~discord.Asset`: Returns the default avatar for a given user."""
        raise NotImplementedError

    @property
    def display_avatar(self) -> Asset:
        """:class:`~discord.Asset`: Returns the user's display avatar.

        For regular users this is just their default avatar or uploaded avatar.

        .. versionadded:: 2.0
        """
        raise NotImplementedError

    def mentioned_in(self, message: Message) -> bool:
        """Checks if the user is mentioned in the specified message.

        Parameters
        -----------
        message: :class:`~discord.Message`
            The message to check if you're mentioned in.

        Returns
        -------
        :class:`bool`
            Indicates if the user is mentioned in the message.
        """
        raise NotImplementedError


class PrivateChannel:
    """An ABC that details the common operations on a private Discord channel.

    The following implement this ABC:

    - :class:`~discord.DMChannel`
    - :class:`~discord.GroupChannel`

    This ABC must also implement :class:`~discord.abc.Snowflake`.

    Attributes
    -----------
    me: :class:`~discord.ClientUser`
        The user presenting yourself.
    """

    __slots__ = ()

    id: int
    me: ClientUser

    def _add_call(self, **kwargs):
        raise NotImplementedError

    def _update(self, *args) -> None:
        raise NotImplementedError


class _Overwrites:
    __slots__ = ("id", "allow", "deny", "type")

    ROLE = 0
    MEMBER = 1

    def __init__(self, data: PermissionOverwritePayload):
        self.id: int = int(data["id"])
        self.allow: int = int(data.get("allow", 0))
        self.deny: int = int(data.get("deny", 0))
        self.type: OverwriteType = data["type"]

    def _asdict(self) -> PermissionOverwritePayload:
        return {
            "id": self.id,
            "allow": str(self.allow),
            "deny": str(self.deny),
            "type": self.type,
        }

    def is_role(self) -> bool:
        return self.type == 0

    def is_member(self) -> bool:
        return self.type == 1


class GuildChannel:
    """An ABC that details the common operations on a Discord guild channel.

    The following implement this ABC:

    - :class:`~discord.TextChannel`
    - :class:`~discord.VoiceChannel`

    This ABC must also implement :class:`~discord.abc.Snowflake`.

    Attributes
    -----------
    name: :class:`str`
        The channel name.
    guild: :class:`~discord.Guild`
        The guild the channel belongs to.
    position: :class:`int`
        The position in the channel list. This is a number that starts at 0.
        e.g. the top channel is position 0.
    """

    __slots__ = ()

    id: int
    name: str
    guild: Guild
    type: ChannelType
    position: int
    category_id: Optional[int]
    _state: ConnectionState
    _overwrites: List[_Overwrites]

    if TYPE_CHECKING:

        def __init__(
            self, *, state: ConnectionState, guild: Guild, data: GuildChannelPayload
        ): ...

    def __str__(self) -> str:
        return self.name

    @property
    def _sorting_bucket(self) -> int:
        raise NotImplementedError

    def _update(self, guild: Guild, data: Dict[str, Any]) -> None:
        raise NotImplementedError

    async def _move(
        self,
        position: int,
        parent_id: Optional[Any] = None,
        lock_permissions: bool = False,
        *,
        reason: Optional[str],
    ) -> None:
        if position < 0:
            raise ValueError("Channel position cannot be less than 0.")

        http = self._state.http
        bucket = self._sorting_bucket
        channels: List[GuildChannel] = [
            c for c in self.guild.channels if c._sorting_bucket == bucket
        ]

        channels.sort(key=lambda c: c.position)

        try:
            # remove ourselves from the channel list
            channels.remove(self)
        except ValueError:
            # not there somehow lol
            return
        else:
            index = next(
                (i for i, c in enumerate(channels) if c.position >= position),
                len(channels),
            )
            # add ourselves at our designated position
            channels.insert(index, self)

        payload = []
        for index, c in enumerate(channels):
            d: Dict[str, Any] = {"id": c.id, "position": index}
            if parent_id is not _undefined and c.id == self.id:
                d.update(parent_id=parent_id, lock_permissions=lock_permissions)
            payload.append(d)

        await http.bulk_channel_update(self.guild.id, payload, reason=reason)

    def _fill_overwrites(self, data: GuildChannelPayload) -> None:
        self._overwrites = []
        everyone_index = 0
        everyone_id = self.guild.id

        for index, overridden in enumerate(data.get("permission_overwrites", [])):
            overwrite = _Overwrites(overridden)
            self._overwrites.append(overwrite)

            if overwrite.type == _Overwrites.MEMBER:
                continue

            if overwrite.id == everyone_id:
                # the @everyone role is not guaranteed to be the first one
                # in the list of permission overwrites, however the permission
                # resolution code kind of requires that it is the first one in
                # the list since it is special. So we need the index so we can
                # swap it to be the first one.
                everyone_index = index

        # do the swap
        tmp = self._overwrites
        if tmp:
            tmp[everyone_index], tmp[0] = tmp[0], tmp[everyone_index]

    async def delete(self, *, reason: Optional[str] = None) -> None:
        """|coro|

        Deletes the channel.

        You must have :attr:`~discord.Permissions.manage_channels` to do this.

        Parameters
        -----------
        reason: Optional[:class:`str`]
            The reason for deleting this channel.
            Shows up on the audit log.

        Raises
        -------
        ~discord.Forbidden
            You do not have proper permissions to delete the channel.
        ~discord.NotFound
            The channel was not found or was already deleted.
        ~discord.HTTPException
            Deleting the channel failed.
        """
        await self._state.http.delete_channel(self.id, reason=reason)


class Messageable:
    """An ABC that details the common operations on a model that can send messages.

    The following implement this ABC:

    - :class:`~discord.TextChannel`
    - :class:`~discord.DMChannel`
    - :class:`~discord.User`
    - :class:`~discord.Member`
    - :class:`~discord.ext.commands.Context`
    - :class:`~discord.Thread`
    """

    __slots__ = ()
    _state: ConnectionState

    async def _get_channel(self) -> MessageableChannel:
        raise NotImplementedError

    async def fetch_message(self, id: int, /) -> Message:
        """|coro|

        Retrieves a single :class:`~discord.Message` from the destination.

        Parameters
        ------------
        id: :class:`int`
            The message ID to look for.

        Raises
        --------
        ~discord.NotFound
            The specified message was not found.
        ~discord.Forbidden
            You do not have the permissions required to get a message.
        ~discord.HTTPException
            Retrieving the message failed.

        Returns
        --------
        :class:`~discord.Message`
            The message asked for.
        """
        channel = await self._get_channel()
        data = await self._state.http.get_message(channel.id, id)
        return self._state.create_message(channel=channel, data=data)

    async def ack(self) -> None:
        """|coro|

        Marks every message in this channel as read.

        .. versionadded:: 1.9

        Raises
        -------
        ~discord.HTTPException
            Acking the channel failed.
        """
        channel = await self._get_channel()
        await channel.read_state.ack(
            channel.last_message_id or utils.time_snowflake(utils.utcnow())
        )

    async def unack(self, *, mention_count: Optional[int] = None) -> None:
        """|coro|

        Marks every message in this channel as unread.
        This manually sets the read state to a message ID of 0.

        .. versionadded:: 2.1

        Parameters
        -----------
        mention_count: Optional[:class:`int`]
            The mention count to set the channel read state to.

        Raises
        -------
        ~discord.HTTPException
            Unacking the channel failed.
        """
        channel = await self._get_channel()
        await channel.read_state.ack(0, manual=True, mention_count=mention_count)

    async def ack_pins(self) -> None:
        """|coro|

        Marks a channel's pins as viewed.

        .. versionadded:: 1.9

        Raises
        -------
        ~discord.HTTPException
            Acking the pinned messages failed.
        """
        channel = await self._get_channel()
        await self._state.http.ack_pins(channel.id)

    async def pins(self) -> List[Message]:
        """|coro|

        Retrieves all messages that are currently pinned in the channel.

        .. note::

            Due to a limitation with the Discord API, the :class:`.Message`
            objects returned by this method do not contain complete
            :attr:`.Message.reactions` data.

        Raises
        -------
        ~discord.Forbidden
            You do not have the permission to retrieve pinned messages.
        ~discord.HTTPException
            Retrieving the pinned messages failed.

        Returns
        --------
        List[:class:`~discord.Message`]
            The messages that are currently pinned.
        """
        channel = await self._get_channel()
        state = self._state
        data = await state.http.pins_from(channel.id)
        return [state.create_message(channel=channel, data=m) for m in data]

    async def history(
        self,
        *,
        limit: Optional[int] = 100,
        before: Optional[SnowflakeTime] = None,
        after: Optional[SnowflakeTime] = None,
        around: Optional[SnowflakeTime] = None,
        oldest_first: Optional[bool] = None,
    ) -> AsyncIterator[Message]:
        """Returns an :term:`asynchronous iterator` that enables receiving the destination's message history.

        You must have :attr:`~discord.Permissions.read_message_history` to do this.

        Examples
        ---------

        Usage ::

            counter = 0
            async for message in channel.history(limit=200):
                if message.author == client.user:
                    counter += 1

        Flattening into a list: ::

            messages = [message async for message in channel.history(limit=123)]
            # messages is now a list of Message...

        All parameters are optional.

        Parameters
        -----------
        limit: Optional[:class:`int`]
            The number of messages to retrieve.
            If ``None``, retrieves every message in the channel. Note, however,
            that this would make it a slow operation.
        before: Optional[Union[:class:`~discord.abc.Snowflake`, :class:`datetime.datetime`]]
            Retrieve messages before this date or message.
            If a datetime is provided, it is recommended to use a UTC aware datetime.
            If the datetime is naive, it is assumed to be local time.
        after: Optional[Union[:class:`~discord.abc.Snowflake`, :class:`datetime.datetime`]]
            Retrieve messages after this date or message.
            If a datetime is provided, it is recommended to use a UTC aware datetime.
            If the datetime is naive, it is assumed to be local time.
        around: Optional[Union[:class:`~discord.abc.Snowflake`, :class:`datetime.datetime`]]
            Retrieve messages around this date or message.
            If a datetime is provided, it is recommended to use a UTC aware datetime.
            If the datetime is naive, it is assumed to be local time.
            When using this argument, the maximum limit is 101. Note that if the limit is an
            even number then this will return at most limit + 1 messages.
        oldest_first: Optional[:class:`bool`]
            If set to ``True``, return messages in oldest->newest order. Defaults to ``True`` if
            ``after`` is specified, otherwise ``False``.

        Raises
        ------
        ~discord.Forbidden
            You do not have permissions to get channel message history.
        ~discord.HTTPException
            The request to get message history failed.

        Yields
        -------
        :class:`~discord.Message`
            The message with the message data parsed.
        """

        async def _around_strategy(
            retrieve: int, around: Optional[Snowflake], limit: Optional[int]
        ):
            if not around:
                return [], None, 0

            around_id = around.id if around else None
            data = await self._state.http.logs_from(
                channel.id, retrieve, around=around_id
            )

            return data, None, 0

        async def _after_strategy(
            retrieve: int, after: Optional[Snowflake], limit: Optional[int]
        ):
            after_id = after.id if after else None
            data = await self._state.http.logs_from(
                channel.id, retrieve, after=after_id
            )

            if data:
                if limit is not None:
                    limit -= len(data)

                after = Object(id=int(data[0]["id"]))

            return data, after, limit

        async def _before_strategy(
            retrieve: int, before: Optional[Snowflake], limit: Optional[int]
        ):
            before_id = before.id if before else None
            data = await self._state.http.logs_from(
                channel.id, retrieve, before=before_id
            )

            if data:
                if limit is not None:
                    limit -= len(data)

                before = Object(id=int(data[-1]["id"]))

            return data, before, limit

        if isinstance(before, datetime):
            before = Object(id=utils.time_snowflake(before, high=False))
        if isinstance(after, datetime):
            after = Object(id=utils.time_snowflake(after, high=True))
        if isinstance(around, datetime):
            around = Object(id=utils.time_snowflake(around))

        if oldest_first is None:
            reverse = after is not None
        else:
            reverse = oldest_first

        after = after or OLDEST_OBJECT
        predicate = None

        if around:
            if limit is None:
                raise ValueError("history does not support around with limit=None")
            if limit > 101:
                raise ValueError(
                    "history max limit 101 when specifying around parameter"
                )

            # Strange Discord quirk
            limit = 100 if limit == 101 else limit

            strategy, state = _around_strategy, around

            if before and after:
                predicate = lambda m: after.id < int(m["id"]) < before.id
            elif before:
                predicate = lambda m: int(m["id"]) < before.id
            elif after:
                predicate = lambda m: after.id < int(m["id"])
        elif reverse:
            strategy, state = _after_strategy, after
            if before:
                predicate = lambda m: int(m["id"]) < before.id
        else:
            strategy, state = _before_strategy, before
            if after and after != OLDEST_OBJECT:
                predicate = lambda m: int(m["id"]) > after.id

        channel = await self._get_channel()

        while True:
            retrieve = 100 if limit is None else min(limit, 100)
            if retrieve < 1:
                return

            data, state, limit = await strategy(retrieve, state, limit)

            if reverse:
                data = reversed(data)
            if predicate:
                data = filter(predicate, data)

            count = 0

            for count, raw_message in enumerate(data, 1):
                yield self._state.create_message(channel=channel, data=raw_message)

            if count < 100:
                # There's no data left after this
                break

    def slash_commands(
        self,
        query: Optional[str] = None,
        *,
        limit: Optional[int] = None,
        command_ids: Optional[Collection[int]] = None,
        application: Optional[Snowflake] = None,
        with_applications: bool = True,
    ) -> AsyncIterator[SlashCommand]:
        """Returns a :term:`asynchronous iterator` of the slash commands available in the channel.

        Examples
        ---------

        Usage ::

            async for command in channel.slash_commands():
                print(command.name)

        Flattening into a list ::

            commands = [command async for command in channel.slash_commands()]
            # commands is now a list of SlashCommand...

        All parameters are optional.

        Parameters
        ----------
        query: Optional[:class:`str`]
            The query to search for. Specifying this limits results to 25 commands max.

            This parameter is faked if ``application`` is specified.
        limit: Optional[:class:`int`]
            The maximum number of commands to send back. Defaults to 0 if ``command_ids`` is passed, else 25.
            If ``None``, returns all commands.

            This parameter is faked if ``application`` is specified.
        command_ids: Optional[List[:class:`int`]]
            List of up to 100 command IDs to search for. If the command doesn't exist, it won't be returned.

            If ``limit`` is passed alongside this parameter, this parameter will serve as a "preferred commands" list.
            This means that the endpoint will return the found commands + up to ``limit`` more, if available.
        application: Optional[:class:`~discord.abc.Snowflake`]
            Whether to return this application's commands. Always set to DM recipient in a private channel context.
        with_applications: :class:`bool`
            Whether to include applications in the response. Defaults to ``True``.

        Raises
        ------
        TypeError
            Both query and command_ids are passed.
            Attempted to fetch commands in a DM with a non-bot user.
        ValueError
            The limit was not greater than or equal to 0.
        HTTPException
            Getting the commands failed.
        ~discord.Forbidden
            You do not have permissions to get the commands.
        ~discord.HTTPException
            The request to get the commands failed.

        Yields
        -------
        :class:`~discord.SlashCommand`
            A slash command.
        """
        return _handle_commands(
            self,
            ApplicationCommandType.chat_input,
            query=query,
            limit=limit,
            command_ids=command_ids,
            application=application,
            with_applications=with_applications,
        )

    def user_commands(
        self,
        query: Optional[str] = None,
        *,
        limit: Optional[int] = None,
        command_ids: Optional[Collection[int]] = None,
        application: Optional[Snowflake] = None,
        with_applications: bool = True,
    ) -> AsyncIterator[UserCommand]:
        """Returns a :term:`asynchronous iterator` of the user commands available to use on the user.

        Examples
        ---------

        Usage ::

            async for command in user.user_commands():
                print(command.name)

        Flattening into a list ::

            commands = [command async for command in user.user_commands()]
            # commands is now a list of UserCommand...

        All parameters are optional.

        Parameters
        ----------
        query: Optional[:class:`str`]
            The query to search for. Specifying this limits results to 25 commands max.

            This parameter is faked if ``application`` is specified.
        limit: Optional[:class:`int`]
            The maximum number of commands to send back. Defaults to 0 if ``command_ids`` is passed, else 25.
            If ``None``, returns all commands.

            This parameter is faked if ``application`` is specified.
        command_ids: Optional[List[:class:`int`]]
            List of up to 100 command IDs to search for. If the command doesn't exist, it won't be returned.

            If ``limit`` is passed alongside this parameter, this parameter will serve as a "preferred commands" list.
            This means that the endpoint will return the found commands + up to ``limit`` more, if available.
        application: Optional[:class:`~discord.abc.Snowflake`]
            Whether to return this application's commands. Always set to DM recipient in a private channel context.
        with_applications: :class:`bool`
            Whether to include applications in the response. Defaults to ``True``.

        Raises
        ------
        TypeError
            Both query and command_ids are passed.
            Attempted to fetch commands in a DM with a non-bot user.
        ValueError
            The limit was not greater than or equal to 0.
        HTTPException
            Getting the commands failed.
        ~discord.Forbidden
            You do not have permissions to get the commands.
        ~discord.HTTPException
            The request to get the commands failed.

        Yields
        -------
        :class:`~discord.UserCommand`
            A user command.
        """
        return _handle_commands(
            self,
            ApplicationCommandType.user,
            query=query,
            limit=limit,
            command_ids=command_ids,
            application=application,
            with_applications=with_applications,
        )


class Connectable(Protocol):
    """An ABC that details the common operations on a channel that can
    connect to a voice server.

    The following implement this ABC:

    - :class:`~discord.VoiceChannel`
    - :class:`~discord.DMChannel`
    - :class:`~discord.User`
    - :class:`~discord.Member`
    """

    __slots__ = ()
    _state: ConnectionState

    async def _get_channel(self) -> VocalChannel:
        raise NotImplementedError
