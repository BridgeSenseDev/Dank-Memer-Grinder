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
import io
from os import PathLike
from typing import (
    AsyncIterator,
    Dict,
    Collection,
    TYPE_CHECKING,
    Union,
    List,
    Optional,
    Any,
    Callable,
    Tuple,
    ClassVar,
    Type,
)

from . import utils
from .abc import _handle_commands
from .channel import PartialMessageable
from .commands import MessageCommand
from .components import _component_factory
from .embeds import Embed
from .emoji import Emoji
from .enums import MessageType, ChannelType, ApplicationCommandType, try_enum
from .file import File
from .flags import MessageFlags, AttachmentFlags
from .guild import Guild
from .interactions import Interaction
from .mixins import Hashable
from .partial_emoji import PartialEmoji
from .utils import MISSING

if TYPE_CHECKING:
    from typing_extensions import Self

    from .types.message import (
        Message as MessagePayload,
        Attachment as AttachmentPayload,
        MessageReference as MessageReferencePayload,
        MessageSearchResult as MessageSearchResultPayload,
    )

    from .types.interactions import MessageInteraction as MessageInteractionPayload

    from .types.components import MessageActionRow as ComponentPayload
    from .types.user import User as UserPayload
    from .types.embed import Embed as EmbedPayload
    from .types.gateway import MessageUpdateEvent
    from .abc import Snowflake
    from .abc import GuildChannel, MessageableChannel
    from .components import ActionRow
    from .state import ConnectionState
    from .user import User

    EmojiInputType = Union[Emoji, PartialEmoji, str]


__all__ = (
    "Attachment",
    "Message",
    "PartialMessage",
    "MessageReference",
)


class Attachment(Hashable):
    """Represents an attachment from Discord.

    .. container:: operations

        .. describe:: str(x)

            Returns the URL of the attachment.

        .. describe:: x == y

            Checks if the attachment is equal to another attachment.

        .. describe:: x != y

            Checks if the attachment is not equal to another attachment.

        .. describe:: hash(x)

            Returns the hash of the attachment.

    .. versionchanged:: 1.7
        Attachment can now be casted to :class:`str` and is hashable.

    Attributes
    ------------
    id: :class:`int`
        The attachment ID.
    size: :class:`int`
        The attachment size in bytes.
    height: Optional[:class:`int`]
        The attachment's height, in pixels. Only applicable to images and videos.
    width: Optional[:class:`int`]
        The attachment's width, in pixels. Only applicable to images and videos.
    filename: :class:`str`
        The attachment's filename.
    url: :class:`str`
        The attachment URL. If the message this attachment was attached
        to is deleted, then this will 404.
    proxy_url: :class:`str`
        The proxy URL. This is a cached version of the :attr:`~Attachment.url` in the
        case of images. When the message is deleted, this URL might be valid for a few
        minutes or not valid at all.
    content_type: Optional[:class:`str`]
        The attachment's `media type <https://en.wikipedia.org/wiki/Media_type>`_

        .. versionadded:: 1.7
    description: Optional[:class:`str`]
        The attachment's description. Only applicable to images.

        .. versionadded:: 2.0
    ephemeral: :class:`bool`
        Whether the attachment is ephemeral.

        .. versionadded:: 2.0
    duration: Optional[:class:`float`]
        The duration of the audio file in seconds. Returns ``None`` if it's not a voice message.

        .. versionadded:: 2.1
    waveform: Optional[:class:`bytes`]
        The waveform (amplitudes) of the audio in bytes. Returns ``None`` if it's not a voice message.

        .. versionadded:: 2.1
    """

    __slots__ = (
        "id",
        "size",
        "height",
        "width",
        "filename",
        "url",
        "proxy_url",
        "_http",
        "content_type",
        "description",
        "ephemeral",
        "duration",
        "waveform",
        "_flags",
    )

    def __init__(self, *, data: AttachmentPayload, state: ConnectionState):
        self.id: int = int(data["id"])
        self.size: int = data["size"]
        self.height: Optional[int] = data.get("height")
        self.width: Optional[int] = data.get("width")
        self.filename: str = data["filename"]
        self.url: str = data["url"]
        self.proxy_url: str = data["proxy_url"]
        self._http = state.http
        self.content_type: Optional[str] = data.get("content_type")
        self.description: Optional[str] = data.get("description")
        self.ephemeral: bool = data.get("ephemeral", False)
        self.duration: Optional[float] = data.get("duration_secs")

        waveform = data.get("waveform")
        self.waveform: Optional[bytes] = (
            utils._base64_to_bytes(waveform) if waveform is not None else None
        )

        self._flags: int = data.get("flags", 0)

    @property
    def flags(self) -> AttachmentFlags:
        """:class:`AttachmentFlags`: The attachment's flags."""
        return AttachmentFlags._from_value(self._flags)

    def is_spoiler(self) -> bool:
        """:class:`bool`: Whether this attachment contains a spoiler."""
        return self.filename.startswith("SPOILER_")

    def is_voice_message(self) -> bool:
        """:class:`bool`: Whether this attachment is a voice message.

        .. versionadded:: 2.1
        """
        return self.waveform is not None

    def __repr__(self) -> str:
        return f"<Attachment id={self.id} filename={self.filename!r} url={self.url!r}>"

    def __str__(self) -> str:
        return self.url or ""

    async def save(
        self,
        fp: Union[io.BufferedIOBase, PathLike[Any]],
        *,
        seek_begin: bool = True,
        use_cached: bool = False,
    ) -> int:
        """|coro|

        Saves this attachment into a file-like object.

        Parameters
        -----------
        fp: Union[:class:`io.BufferedIOBase`, :class:`os.PathLike`]
            The file-like object to save this attachment to or the filename
            to use. If a filename is passed then a file is created with that
            filename and used instead.
        seek_begin: :class:`bool`
            Whether to seek to the beginning of the file after saving is
            successfully done.
        use_cached: :class:`bool`
            Whether to use :attr:`proxy_url` rather than :attr:`url` when downloading
            the attachment. This will allow attachments to be saved after deletion
            more often, compared to the regular URL which is generally deleted right
            after the message is deleted. Note that this can still fail to download
            deleted attachments if too much time has passed and it does not work
            on some types of attachments.

        Raises
        --------
        HTTPException
            Saving the attachment failed.
        NotFound
            The attachment was deleted.

        Returns
        --------
        :class:`int`
            The number of bytes written.
        """
        data = await self.read(use_cached=use_cached)
        if isinstance(fp, io.BufferedIOBase):
            written = fp.write(data)
            if seek_begin:
                fp.seek(0)
            return written
        else:
            with open(fp, "wb") as f:
                return f.write(data)

    async def read(self, *, use_cached: bool = False) -> bytes:
        """|coro|

        Retrieves the content of this attachment as a :class:`bytes` object.

        .. versionadded:: 1.1

        Parameters
        -----------
        use_cached: :class:`bool`
            Whether to use :attr:`proxy_url` rather than :attr:`url` when downloading
            the attachment. This will allow attachments to be saved after deletion
            more often, compared to the regular URL which is generally deleted right
            after the message is deleted. Note that this can still fail to download
            deleted attachments if too much time has passed and it does not work
            on some types of attachments.

        Raises
        ------
        HTTPException
            Downloading the attachment failed.
        Forbidden
            You do not have permissions to access this attachment
        NotFound
            The attachment was deleted.

        Returns
        -------
        :class:`bytes`
            The contents of the attachment.
        """
        url = self.proxy_url if use_cached else self.url
        data = await self._http.get_from_cdn(url)
        return data

    async def to_file(
        self,
        *,
        filename: Optional[str] = MISSING,
        description: Optional[str] = MISSING,
        use_cached: bool = False,
        spoiler: bool = False,
    ) -> File:
        """|coro|

        Converts the attachment into a :class:`File` suitable for sending via
        :meth:`abc.Messageable.send`.

        .. versionadded:: 1.3

        Parameters
        -----------
        filename: Optional[:class:`str`]
            The filename to use for the file. If not specified then the filename
            of the attachment is used instead.

            .. versionadded:: 2.0
        description: Optional[:class:`str`]
            The description to use for the file. If not specified then the
            description of the attachment is used instead.

            .. versionadded:: 2.0
        use_cached: :class:`bool`
            Whether to use :attr:`proxy_url` rather than :attr:`url` when downloading
            the attachment. This will allow attachments to be saved after deletion
            more often, compared to the regular URL which is generally deleted right
            after the message is deleted. Note that this can still fail to download
            deleted attachments if too much time has passed and it does not work
            on some types of attachments.

            .. versionadded:: 1.4
        spoiler: :class:`bool`
            Whether the file is a spoiler.

            .. versionadded:: 1.4

        Raises
        ------
        HTTPException
            Downloading the attachment failed.
        Forbidden
            You do not have permissions to access this attachment
        NotFound
            The attachment was deleted.

        Returns
        -------
        :class:`File`
            The attachment as a file suitable for sending.
        """

        data = await self.read(use_cached=use_cached)
        file_filename = filename if filename is not MISSING else self.filename
        file_description = (
            description if description is not MISSING else self.description
        )
        return File(
            io.BytesIO(data),
            filename=file_filename,
            description=file_description,
            spoiler=spoiler,
        )

    def to_dict(self) -> AttachmentPayload:
        result: AttachmentPayload = {
            "filename": self.filename,
            "id": self.id,
            "proxy_url": self.proxy_url,
            "size": self.size,
            "url": self.url,
            "spoiler": self.is_spoiler(),
        }
        if self.height:
            result["height"] = self.height
        if self.width:
            result["width"] = self.width
        if self.content_type:
            result["content_type"] = self.content_type
        if self.description is not None:
            result["description"] = self.description
        return result


class MessageReference:
    """Represents a reference to a :class:`~discord.Message`.

    .. versionadded:: 1.5

    .. versionchanged:: 1.6
        This class can now be constructed by users.

    Attributes
    -----------
    message_id: Optional[:class:`int`]
        The id of the message referenced.
    channel_id: :class:`int`
        The channel id of the message referenced.
    guild_id: Optional[:class:`int`]
        The guild id of the message referenced.
    fail_if_not_exists: :class:`bool`
        Whether replying to the referenced message should raise :class:`HTTPException`
        if the message no longer exists or Discord could not fetch the message.

        .. versionadded:: 1.7
    """

    __slots__ = (
        "message_id",
        "channel_id",
        "guild_id",
        "fail_if_not_exists",
        "resolved",
        "_state",
    )

    def __init__(
        self,
        *,
        message_id: int,
        channel_id: int,
        guild_id: Optional[int] = None,
        fail_if_not_exists: bool = True,
    ):
        self._state: Optional[ConnectionState] = None
        self.message_id: Optional[int] = message_id
        self.channel_id: int = channel_id
        self.guild_id: Optional[int] = guild_id
        self.fail_if_not_exists: bool = fail_if_not_exists

    @classmethod
    def with_state(cls, state: ConnectionState, data: MessageReferencePayload) -> Self:
        self = cls.__new__(cls)
        self.message_id = utils._get_as_snowflake(data, "message_id")
        self.channel_id = int(data["channel_id"])
        self.guild_id = utils._get_as_snowflake(data, "guild_id")
        self.fail_if_not_exists = data.get("fail_if_not_exists", True)
        self._state = state
        self.resolved = None
        return self

    @classmethod
    def from_message(
        cls, message: PartialMessage, *, fail_if_not_exists: bool = True
    ) -> Self:
        """Creates a :class:`MessageReference` from an existing :class:`~discord.Message`.

        .. versionadded:: 1.6

        Parameters
        ----------
        message: :class:`~discord.Message`
            The message to be converted into a reference.
        fail_if_not_exists: :class:`bool`
            Whether replying to the referenced message should raise :class:`HTTPException`
            if the message no longer exists or Discord could not fetch the message.

            .. versionadded:: 1.7

        Returns
        -------
        :class:`MessageReference`
            A reference to the message.
        """
        self = cls(
            message_id=message.id,
            channel_id=message.channel.id,
            guild_id=getattr(message.guild, "id", None),
            fail_if_not_exists=fail_if_not_exists,
        )
        self._state = message._state
        return self

    @property
    def cached_message(self) -> Optional[Message]:
        """Optional[:class:`~discord.Message`]: The cached message, if found in the internal message cache."""
        return self._state and self._state._get_message(self.message_id)

    @property
    def jump_url(self) -> str:
        """:class:`str`: Returns a URL that allows the client to jump to the referenced message.

        .. versionadded:: 1.7
        """
        guild_id = self.guild_id if self.guild_id is not None else "@me"
        return f"https://discord.com/channels/{guild_id}/{self.channel_id}/{self.message_id}"

    def __repr__(self) -> str:
        return (
            "<MessageReference"
            f" message_id={self.message_id!r} channel_id={self.channel_id!r} guild_id={self.guild_id!r}>"
        )

    def to_dict(self) -> MessageReferencePayload:
        result: Dict[str, Any] = (
            {"message_id": self.message_id} if self.message_id is not None else {}
        )
        result["channel_id"] = self.channel_id
        if self.guild_id is not None:
            result["guild_id"] = self.guild_id
        if self.fail_if_not_exists is not None:
            result["fail_if_not_exists"] = self.fail_if_not_exists
        return result  # type: ignore # Type checker doesn't understand these are the same

    to_message_reference_dict = to_dict


def flatten_handlers(cls: Type[Message]) -> Type[Message]:
    prefix = len("_handle_")
    handlers = [
        (key[prefix:], value)
        for key, value in cls.__dict__.items()
        if key.startswith("_handle_") and key != "_handle_member"
    ]

    cls._HANDLERS = handlers
    cls._CACHED_SLOTS = [attr for attr in cls.__slots__ if attr.startswith("_cs_")]
    return cls


class PartialMessage(Hashable):
    """Represents a partial message to aid with working messages when only
    a message and channel ID are present.

    There are two ways to construct this class. The first one is through
    the constructor itself, and the second is via the following:

    - :meth:`TextChannel.get_partial_message`
    - :meth:`Thread.get_partial_message`
    - :meth:`DMChannel.get_partial_message`

    Note that this class is trimmed down and has no rich attributes.

    .. versionadded:: 1.6

    .. container:: operations

        .. describe:: x == y

            Checks if two partial messages are equal.

        .. describe:: x != y

            Checks if two partial messages are not equal.

        .. describe:: hash(x)

            Returns the partial message's hash.

    Attributes
    -----------
    channel: Union[:class:`PartialMessageable`, :class:`TextChannel`, :class:`Thread`, :class:`DMChannel`]
        The channel associated with this partial message.
    id: :class:`int`
        The message ID.
    guild_id: Optional[:class:`int`]
        The ID of the guild that the partial message belongs to, if applicable.

        .. versionadded:: 2.1
    guild: Optional[:class:`Guild`]
        The guild that the partial message belongs to, if applicable.
    """

    __slots__ = ("channel", "id", "_state", "guild_id", "guild")

    def __init__(self, *, channel: MessageableChannel, id: int) -> None:
        if not isinstance(channel, PartialMessageable) and channel.type not in (
            ChannelType.text,
            ChannelType.voice,
            ChannelType.stage_voice,
            ChannelType.news,
            ChannelType.private,
            ChannelType.news_thread,
            ChannelType.public_thread,
            ChannelType.private_thread,
        ):
            raise TypeError(
                "expected PartialMessageable, TextChannel,"
                f" DMChannel or Thread not {type(channel)!r}"
            )

        self.channel: MessageableChannel = channel
        self._state: ConnectionState = channel._state
        self.id: int = id

        self.guild: Optional[Guild] = getattr(channel, "guild", None)
        self.guild_id: Optional[int] = self.guild.id if self.guild else None
        if hasattr(channel, "guild_id"):
            if self.guild_id is not None:
                channel.guild_id = self.guild_id  # type: ignore
            else:
                self.guild_id = channel.guild_id  # type: ignore

    def _update(self, data: MessageUpdateEvent) -> None:
        # This is used for duck typing purposes.
        # Just do nothing with the data.
        pass

    def __repr__(self) -> str:
        return f"<PartialMessage id={self.id} channel={self.channel!r}>"

    @property
    def created_at(self) -> datetime.datetime:
        """:class:`datetime.datetime`: The partial message's creation time in UTC."""
        return utils.snowflake_time(self.id)

    @property
    def jump_url(self) -> str:
        """:class:`str`: Returns a URL that allows the client to jump to this message."""
        guild_id = getattr(self.guild, "id", "@me")
        return f"https://discord.com/channels/{guild_id}/{self.channel.id}/{self.id}"

    async def ack(
        self, *, manual: bool = False, mention_count: Optional[int] = None
    ) -> None:
        """|coro|

        Marks this message as read.

        .. note::

            This sets the last acknowledged message to this message,
            which will mark acknowledged messages created after this one as unread.

        Parameters
        -----------
        manual: :class:`bool`
            Whether to manually set the channel read state to this message.

            .. versionadded:: 2.1
        mention_count: Optional[:class:`int`]
            The mention count to set the channel read state to. Only applicable for
            manual acknowledgements.

            .. versionadded:: 2.1

        Raises
        -------
        HTTPException
            Acking failed.
        """
        await self.channel.read_state.ack(
            self.id, manual=manual, mention_count=mention_count
        )

    async def unack(self, *, mention_count: Optional[int] = None) -> None:
        """|coro|

        Marks this message as unread.
        This manually sets the read state to the current message's ID - 1.

        .. versionadded:: 2.1

        Parameters
        -----------
        mention_count: Optional[:class:`int`]
            The mention count to set the channel read state to.

        Raises
        -------
        HTTPException
            Unacking failed.
        """
        await self.channel.read_state.ack(
            self.id - 1, manual=True, mention_count=mention_count
        )

    def to_reference(self, *, fail_if_not_exists: bool = True) -> MessageReference:
        """Creates a :class:`~discord.MessageReference` from the current message.

        .. versionadded:: 1.6

        Parameters
        ----------
        fail_if_not_exists: :class:`bool`
            Whether replying using the message reference should raise :class:`HTTPException`
            if the message no longer exists or Discord could not fetch the message.

            .. versionadded:: 1.7

        Returns
        ---------
        :class:`~discord.MessageReference`
            The reference to this message.
        """
        return MessageReference.from_message(
            self, fail_if_not_exists=fail_if_not_exists
        )

    def to_message_reference_dict(self) -> MessageReferencePayload:
        data: MessageReferencePayload = {
            "message_id": self.id,
            "channel_id": self.channel.id,
        }

        if self.guild is not None:
            data["guild_id"] = self.guild.id

        return data


@flatten_handlers
class Message(PartialMessage, Hashable):
    r"""Represents a message from Discord.

    .. container:: operations

        .. describe:: x == y

            Checks if two messages are equal.

        .. describe:: x != y

            Checks if two messages are not equal.

        .. describe:: hash(x)

            Returns the message's hash.

    Attributes
    -----------
    type: :class:`MessageType`
        The type of message. In most cases this should not be checked, but it is helpful
        in cases where it might be a system message for :attr:`system_content`.
    author: Union[:class:`Member`, :class:`abc.User`]
        A :class:`Member` that sent the message. If :attr:`channel` is a
        private channel or the user has the left the guild, then it is a :class:`User` instead.
    content: :class:`str`
        The actual contents of the message.
    nonce: Optional[Union[:class:`str`, :class:`int`]]
        The value used by Discord clients to verify that the message is successfully sent.
        This is not stored long term within Discord's servers and is only used ephemerally.
    embeds: List[:class:`Embed`]
        A list of embeds the message has.
    channel: Union[:class:`TextChannel`, :class:`StageChannel`, :class:`VoiceChannel`, :class:`Thread`, :class:`DMChannel`, :class:`GroupChannel`, :class:`PartialMessageable`]
        The :class:`TextChannel` or :class:`Thread` that the message was sent from.
        Could be a :class:`DMChannel` or :class:`GroupChannel` if it's a private message.
    reference: Optional[:class:`~discord.MessageReference`]
        The message that this message references. This is only applicable to messages of
        type :attr:`MessageType.pins_add`, crossposted messages created by a
        followed channel integration, or message replies.

        .. versionadded:: 1.5
    id: :class:`int`
        The message ID.
    attachments: List[:class:`Attachment`]
        A list of attachments given to a message.
    flags: :class:`MessageFlags`
        Extra features of the message.

        .. versionadded:: 1.3
    components: List[Union[:class:`ActionRow`, :class:`Button`, :class:`SelectMenu`]]
        A list of components in the message.

        .. versionadded:: 2.0
    application_id: Optional[:class:`int`]
        The application ID of the application that created this message if this
        message was sent by an application-owned webhook or an interaction.

        .. versionadded:: 2.0
    guild_id: Optional[:class:`int`]
        The ID of the guild that the partial message belongs to, if applicable.

        .. versionadded:: 2.1
    guild: Optional[:class:`Guild`]
        The guild that the message belongs to, if applicable.
    interaction: Optional[:class:`Interaction`]
        The interaction that this message is a response to.

        .. versionadded:: 2.0
    """

    __slots__ = (
        "content",
        "embeds",
        "author",
        "attachments",
        "nonce",
        "type",
        "flags",
        "reactions",
        "reference",
        "components",
        "interaction",
        "application_id",
    )

    if TYPE_CHECKING:
        _HANDLERS: ClassVar[List[Tuple[str, Callable[..., None]]]]
        _CACHED_SLOTS: ClassVar[List[str]]
        reference: Optional[MessageReference]
        author: User
        components: List[ActionRow]

    def __init__(
        self,
        *,
        state: ConnectionState,
        channel: MessageableChannel,
        data: MessagePayload,
        search_result: Optional[MessageSearchResultPayload] = None,
    ) -> None:
        self.channel: MessageableChannel = channel
        self.id: int = int(data["id"])
        self._state: ConnectionState = state
        self.attachments: List[Attachment] = [
            Attachment(data=a, state=self._state) for a in data["attachments"]
        ]
        self.embeds: List[Embed] = [Embed.from_dict(a) for a in data["embeds"]]
        self.type: MessageType = try_enum(MessageType, data["type"])
        self.flags: MessageFlags = MessageFlags._from_value(data.get("flags", 0))
        self.content: str = data["content"]
        self.nonce: Optional[Union[int, str]] = data.get("nonce")
        self.application_id: Optional[int] = utils._get_as_snowflake(
            data, "application_id"
        )

        try:
            # If the channel doesn't have a guild attribute, we handle that
            self.guild = channel.guild
        except AttributeError:
            guild_id = utils._get_as_snowflake(data, "guild_id")
            if guild_id is not None:
                channel.guild_id = guild_id  # type: ignore
            else:
                guild_id = channel.guild_id  # type: ignore

            self.guild_id: Optional[int] = guild_id
            self.guild = state._get_guild(guild_id)

        self.interaction: Optional[Interaction] = None
        try:
            interaction = data["interaction"]
        except KeyError:
            pass
        else:
            self.interaction = Interaction._from_message(self, **interaction)

        try:
            ref = data["message_reference"]
        except KeyError:
            self.reference = None
        else:
            self.reference = ref = MessageReference.with_state(state, ref)
            try:
                resolved = data["referenced_message"]
            except KeyError:
                pass
            else:
                if resolved:
                    # Right now the channel IDs match but maybe in the future they won't
                    if ref.channel_id == channel.id:
                        chan = channel
                    elif isinstance(channel) and channel.parent_id == ref.channel_id:
                        chan = channel
                    else:
                        chan, _ = state._get_guild_channel(resolved, ref.guild_id)

                    # The channel will be the correct type here
                    ref.resolved = self.__class__(channel=chan, data=resolved, state=state)  # type: ignore

        search_payload = search_result or {}

        for handler in (
            "author",
            "interaction",
            "components",
        ):
            try:
                getattr(self, f"_handle_{handler}")(data[handler])
            except KeyError:
                continue

    def __repr__(self) -> str:
        name = self.__class__.__name__
        return (
            f"<{name} id={self.id} channel={self.channel!r} type={self.type!r} author={self.author!r} flags={self.flags!r}>"
        )

    async def _get_channel(self) -> MessageableChannel:
        return self.channel

    def _try_patch(self, data, key, transform=None) -> None:
        try:
            value = data[key]
        except KeyError:
            pass
        else:
            if transform is None:
                setattr(self, key, value)
            else:
                setattr(self, key, transform(value))

    def _update(self, data: MessageUpdateEvent) -> None:
        # In an update scheme, 'author' key has to be handled before 'member'
        # otherwise they overwrite each other which is undesirable
        # Since there's no good way to do this we have to iterate over every
        # handler rather than iterating over the keys which is a little slower
        for key, handler in self._HANDLERS:
            try:
                value = data[key]
            except KeyError:
                continue
            else:
                handler(self, value)

        # Clear the cached properties
        for attr in self._CACHED_SLOTS:
            try:
                delattr(self, attr)
            except AttributeError:
                pass

    def _handle_flags(self, value: int) -> None:
        self.flags = MessageFlags._from_value(value)

    def _handle_type(self, value: int) -> None:
        self.type = try_enum(MessageType, value)

    def _handle_content(self, value: str) -> None:
        self.content = value

    def _handle_attachments(self, value: List[AttachmentPayload]) -> None:
        self.attachments = [Attachment(data=a, state=self._state) for a in value]

    def _handle_embeds(self, value: List[EmbedPayload]) -> None:
        self.embeds = [Embed.from_dict(data) for data in value]

    def _handle_nonce(self, value: Union[str, int]) -> None:
        self.nonce = value

    def _handle_author(self, author: UserPayload) -> None:
        self.author = self._state.store_user(author, cache=True)
        if isinstance(self.guild, Guild):
            found = self._state.get_user(self.author.id)
            if found is not None:
                self.author = found

    def _handle_components(self, data: List[ComponentPayload]) -> None:
        self.components = []
        for component_data in data:
            component = _component_factory(component_data, self)
            if component is not None:
                self.components.append(component)

    def _handle_interaction(self, data: MessageInteractionPayload):
        self.interaction = Interaction._from_message(self, **data)

    def _rebind_cached_references(
        self,
        new_guild: Guild,
        new_channel: Union[GuildChannel, PartialMessageable],
    ) -> None:
        self.guild = new_guild
        self.channel = new_channel  # type: ignore # Not all "GuildChannel" are messageable at the moment

    def is_acked(self) -> bool:
        """:class:`bool`: Whether the message has been marked as read.

        .. versionadded:: 2.1
        """
        read_state = self._state.get_read_state(self.channel.id)
        return (
            read_state.last_acked_id >= self.id if read_state.last_acked_id else False
        )

    def message_commands(
        self,
        query: Optional[str] = None,
        *,
        limit: Optional[int] = None,
        command_ids: Optional[Collection[int]] = None,
        application: Optional[Snowflake] = None,
        with_applications: bool = True,
    ) -> AsyncIterator[MessageCommand]:
        """Returns a :term:`asynchronous iterator` of the message commands available to use on the message.

        Examples
        ---------

        Usage ::

            async for command in message.message_commands():
                print(command.name)

        Flattening into a list ::

            commands = [command async for command in message.message_commands()]
            # commands is now a list of MessageCommand...

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
        :class:`.MessageCommand`
            A message command.
        """
        return _handle_commands(
            self,
            ApplicationCommandType.message,
            query=query,
            limit=limit,
            command_ids=command_ids,
            application=application,
            with_applications=with_applications,
            target=self,
        )
