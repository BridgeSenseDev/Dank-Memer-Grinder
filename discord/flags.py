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

from functools import reduce
from operator import or_
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    overload,
)

if TYPE_CHECKING:
    from typing_extensions import Self


__all__ = (
    "Capabilities",
    "SystemChannelFlags",
    "MessageFlags",
    "MemberCacheFlags",
    "ApplicationFlags",
    "ChannelFlags",
    "PaymentSourceFlags",
    "LibraryApplicationFlags",
    "ApplicationDiscoveryFlags",
    "FriendSourceFlags",
    "FriendDiscoveryFlags",
    "OnboardingProgressFlags",
    "MemberFlags",
    "ReadStateFlags",
    "InviteFlags",
    "AttachmentFlags",
)

BF = TypeVar("BF", bound="BaseFlags")


class flag_value:
    def __init__(self, func: Callable[[Any], int]):
        self.flag: int = func(None)
        self.__doc__: Optional[str] = func.__doc__

    @overload
    def __get__(self, instance: None, owner: Type[BF]) -> Self: ...

    @overload
    def __get__(self, instance: BF, owner: Type[BF]) -> bool: ...

    def __get__(self, instance: Optional[BF], owner: Type[BF]) -> Any:
        if instance is None:
            return self
        return instance._has_flag(self.flag)

    def __set__(self, instance: BaseFlags, value: bool) -> None:
        instance._set_flag(self.flag, value)

    def __repr__(self) -> str:
        return f"<flag_value flag={self.flag!r}>"


class alias_flag_value(flag_value):
    pass


def fill_with_flags(*, inverted: bool = False) -> Callable[[Type[BF]], Type[BF]]:
    def decorator(cls: Type[BF]) -> Type[BF]:
        # fmt: off
        cls.VALID_FLAGS = {
            name: value.flag
            for name, value in cls.__dict__.items()
            if isinstance(value, flag_value)
        }
        # fmt: on

        cls.DEFAULT_VALUE = 0

        return cls

    return decorator


# Flags must inherit from this and use the decorator above
class BaseFlags:
    VALID_FLAGS: ClassVar[Dict[str, int]]
    DEFAULT_VALUE: ClassVar[int]

    value: int

    __slots__ = ("value",)

    def __init__(self, **kwargs: bool):
        self.value = self.DEFAULT_VALUE
        for key, value in kwargs.items():
            if key not in self.VALID_FLAGS:
                raise TypeError(f"{key!r} is not a valid flag name.")
            setattr(self, key, value)

    @classmethod
    def _from_value(cls, value):
        self = cls.__new__(cls)
        self.value = value
        return self

    def __or__(self, other: Self) -> Self:
        return self._from_value(self.value | other.value)

    def __and__(self, other: Self) -> Self:
        return self._from_value(self.value & other.value)

    def __xor__(self, other: Self) -> Self:
        return self._from_value(self.value ^ other.value)

    def __ior__(self, other: Self) -> Self:
        self.value |= other.value
        return self

    def __iand__(self, other: Self) -> Self:
        self.value &= other.value
        return self

    def __ixor__(self, other: Self) -> Self:
        self.value ^= other.value
        return self

    def __invert__(self) -> Self:
        max_bits = max(self.VALID_FLAGS.values()).bit_length()
        max_value = -1 + (2**max_bits)
        return self._from_value(self.value ^ max_value)

    def __bool__(self) -> bool:
        return self.value != self.DEFAULT_VALUE

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.value == other.value

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.value)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} value={self.value}>"

    def __iter__(self) -> Iterator[Tuple[str, bool]]:
        for name, value in self.__class__.__dict__.items():
            if isinstance(value, alias_flag_value):
                continue

            if isinstance(value, flag_value):
                yield (name, self._has_flag(value.flag))

    def _has_flag(self, o: int) -> bool:
        return (self.value & o) == o

    def _set_flag(self, o: int, toggle: bool) -> None:
        if toggle is True:
            self.value |= o
        elif toggle is False:
            self.value &= ~o
        else:
            raise TypeError(
                f"Value to set for {self.__class__.__name__} must be a bool."
            )


class ArrayFlags(BaseFlags):
    @classmethod
    def _from_value(cls: Type[Self], value: Sequence[int]) -> Self:
        self = cls.__new__(cls)
        # This is a micro-optimization given the frequency this object can be created.
        # (1).__lshift__ is used in place of lambda x: 1 << x
        # prebinding to a method of a constant rather than define a lambda.
        # Pairing this with map, is essentially equivalent to (1 << x for x in value)
        # reduction using operator.or_ instead of defining a lambda each call
        # Discord sends these starting with a value of 1
        # Rather than subtract 1 from each element prior to left shift,
        # we shift right by 1 once at the end.
        self.value = reduce(or_, map((1).__lshift__, value), 0) >> 1
        return self

    def to_array(self) -> List[int]:
        return [i + 1 for i in range(self.value.bit_length()) if self.value & (1 << i)]


@fill_with_flags()
class Capabilities(BaseFlags):
    """Wraps up the Discord gateway capabilities.

    Capabilities are used to determine what gateway features a client support.

    This is meant to be used internally by the library.

    .. container:: operations

        .. describe:: x == y

            Checks if two capabilities are equal.
        .. describe:: x != y

            Checks if two capabilities are not equal.
        .. describe:: x | y, x |= y

            Returns a capabilities instance with all enabled flags from
            both x and y.

            .. versionadded:: 2.0
        .. describe:: x & y, x &= y

            Returns a capabilities instance with only flags enabled on
            both x and y.

            .. versionadded:: 2.0
        .. describe:: x ^ y, x ^= y

            Returns a capabilities instance with only flags enabled on
            only one of x or y, not on both.

            .. versionadded:: 2.0
        .. describe:: ~x

            Returns a capabilities instance with all flags inverted from x.

            .. versionadded:: 2.0
        .. describe:: hash(x)

               Return the capability's hash.
        .. describe:: iter(x)

               Returns an iterator of ``(name, value)`` pairs. This allows it
               to be, for example, constructed as a dict or a list of pairs.
        .. describe:: bool(b)

            Returns whether any flag is set to ``True``.

    .. versionadded:: 2.0

    Attributes
    -----------
    value: :class:`int`
        The raw value. This value is a bit array field of a 53-bit integer
        representing the currently available flags. You should query
        flags via the properties rather than using this raw value.
    """

    __slots__ = ()

    # The unfortunate thing about capabilities is that while a lot of these options
    # may be useful to the library (i.e. to expose to users for customization),
    # we match the official client's values for anti-spam purposes :(

    @classmethod
    def default(cls: Type[Self]) -> Self:
        """Returns a :class:`Capabilities` with the current value used by the library."""
        return cls._from_value(8189)

    @flag_value
    def lazy_user_notes(self):
        """:class:`bool`: Disable preloading of user notes in READY."""
        return 1 << 0

    @flag_value
    def no_affine_user_ids(self):
        """:class:`bool`: Disable implicit relationship updates."""
        return 1 << 1

    @flag_value
    def versioned_read_states(self):
        """:class:`bool`: Enable versioned read states (change READY ``read_state`` to an object with ``version``/``partial``)."""
        return 1 << 2

    @flag_value
    def versioned_user_guild_settings(self):
        """:class:`bool`: Enable versioned user guild settings (change READY ``user_guild_settings`` to an object with ``version``/``partial``)."""
        return 1 << 3

    @flag_value
    def dedupe_user_objects(self):
        """:class:`bool`: Enable dehydration of the READY payload (move all user objects to a ``users`` array and replace them in various places in the READY payload with ``user_id`` or ``recipient_id``, move member object(s) from initial guild objects to ``merged_members``)."""
        return 1 << 4

    @flag_value
    def prioritized_ready_payload(self):
        """:class:`bool`: Enable prioritized READY payload (enable READY_SUPPLEMENTAL, move ``voice_states`` and ``embedded_activities`` from initial guild objects and ``merged_presences`` from READY, as well as split ``merged_members`` and (sometimes) ``private_channels``/``lazy_private_channels`` between the events)."""
        # Requires self.dedupe_user_objects
        return 1 << 5 | 1 << 4

    @flag_value
    def multiple_guild_experiment_populations(self):
        """:class:`bool`: Handle multiple guild experiment populations (change the fourth entry of arrays in the ``guild_experiments`` array in READY to have an array of population arrays)."""
        return 1 << 6

    @flag_value
    def non_channel_read_states(self):
        """:class:`bool`: Handle non-channel read states (change READY ``read_state`` to include read states tied to server events, server home, and the mobile notification center)."""
        return 1 << 7

    @flag_value
    def auth_token_refresh(self):
        """:class:`bool`: Enable auth token refresh (add ``auth_token?`` to READY; this is sent when Discord wants to change the client's token, and was used for the mfa. token migration)."""
        return 1 << 8

    @flag_value
    def user_settings_proto(self):
        """:class:`bool`: Disable legacy user settings (remove ``user_settings`` from READY and stop sending USER_SETTINGS_UPDATE)."""
        return 1 << 9

    @flag_value
    def client_state_v2(self):
        """:class:`bool`: Enable client caching v2 (move guild properties in guild objects to a ``properties`` subkey and add ``data_mode`` and ``version`` to the objects, as well as change ``client_state`` in IDENTIFY)."""
        return 1 << 10

    @flag_value
    def passive_guild_update(self):
        """:class:`bool`: Enable passive guild update (replace ``CHANNEL_UNREADS_UPDATE`` with ``PASSIVE_UPDATE_V1``, a similar event that includes a ``voice_states`` array and a ``members`` array that includes the members of aforementioned voice states)."""
        return 1 << 11

    @flag_value
    def unknown_12(self):
        """:class:`bool`: Unknown."""
        return 1 << 12


@fill_with_flags(inverted=True)
class SystemChannelFlags(BaseFlags):
    r"""Wraps up a Discord system channel flag value.

    Similar to :class:`Permissions`\, the properties provided are two way.
    You can set and retrieve individual bits using the properties as if they
    were regular bools. This allows you to edit the system flags easily.

    To construct an object you can pass keyword arguments denoting the flags
    to enable or disable.

    .. container:: operations

        .. describe:: x == y

            Checks if two SystemChannelFlags are equal.
        .. describe:: x != y

            Checks if two SystemChannelFlags are not equal.
        .. describe:: x | y, x |= y

            Returns a SystemChannelFlags instance with all enabled flags from
            both x and y.

            .. versionadded:: 2.0
        .. describe:: x & y, x &= y

            Returns a SystemChannelFlags instance with only flags enabled on
            both x and y.

            .. versionadded:: 2.0
        .. describe:: x ^ y, x ^= y

            Returns a SystemChannelFlags instance with only flags enabled on
            only one of x or y, not on both.

            .. versionadded:: 2.0
        .. describe:: ~x

            Returns a SystemChannelFlags instance with all flags inverted from x.

            .. versionadded:: 2.0
        .. describe:: hash(x)

               Return the flag's hash.
        .. describe:: iter(x)

               Returns an iterator of ``(name, value)`` pairs. This allows it
               to be, for example, constructed as a dict or a list of pairs.
        .. describe:: bool(b)

            Returns whether any flag is set to ``True``.

            .. versionadded:: 2.0

    Attributes
    -----------
    value: :class:`int`
        The raw value. This value is a bit array field of a 53-bit integer
        representing the currently available flags. You should query
        flags via the properties rather than using this raw value.
    """

    __slots__ = ()

    # For some reason the flags for system channels are "inverted"
    # Ergo, if they're set then it means "suppress" (off in the GUI toggle)
    # Since this is counter-intuitive from an API perspective and annoying
    # these will be inverted automatically

    def _has_flag(self, o: int) -> bool:
        return (self.value & o) != o

    def _set_flag(self, o: int, toggle: bool) -> None:
        if toggle is True:
            self.value &= ~o
        elif toggle is False:
            self.value |= o
        else:
            raise TypeError("Value to set for SystemChannelFlags must be a bool")


@fill_with_flags()
class MessageFlags(BaseFlags):
    r"""Wraps up a Discord Message flag value.

    See :class:`SystemChannelFlags`.

    .. container:: operations

        .. describe:: x == y

            Checks if two MessageFlags are equal.
        .. describe:: x != y

            Checks if two MessageFlags are not equal.
        .. describe:: x | y, x |= y

            Returns a MessageFlags instance with all enabled flags from
            both x and y.

            .. versionadded:: 2.0
        .. describe:: x & y, x &= y

            Returns a MessageFlags instance with only flags enabled on
            both x and y.

            .. versionadded:: 2.0
        .. describe:: x ^ y, x ^= y

            Returns a MessageFlags instance with only flags enabled on
            only one of x or y, not on both.

            .. versionadded:: 2.0
        .. describe:: ~x

            Returns a MessageFlags instance with all flags inverted from x.

            .. versionadded:: 2.0
        .. describe:: hash(x)

               Return the flag's hash.
        .. describe:: iter(x)

               Returns an iterator of ``(name, value)`` pairs. This allows it
               to be, for example, constructed as a dict or a list of pairs.
        .. describe:: bool(b)

            Returns whether any flag is set to ``True``.

            .. versionadded:: 2.0

    .. versionadded:: 1.3

    Attributes
    -----------
    value: :class:`int`
        The raw value. This value is a bit array field of a 53-bit integer
        representing the currently available flags. You should query
        flags via the properties rather than using this raw value.
    """

    __slots__ = ()

    @flag_value
    def crossposted(self):
        """:class:`bool`: Returns ``True`` if the message is the original crossposted message."""
        return 1

    @flag_value
    def is_crossposted(self):
        """:class:`bool`: Returns ``True`` if the message was crossposted from another channel."""
        return 2

    @flag_value
    def suppress_embeds(self):
        """:class:`bool`: Returns ``True`` if the message's embeds have been suppressed."""
        return 4

    @flag_value
    def source_message_deleted(self):
        """:class:`bool`: Returns ``True`` if the source message for this crosspost has been deleted."""
        return 8

    @flag_value
    def urgent(self):
        """:class:`bool`: Returns ``True`` if the message is an urgent message.

        An urgent message is one sent by Discord Trust and Safety.
        """
        return 16

    @flag_value
    def has_thread(self):
        """:class:`bool`: Returns ``True`` if the message is associated with a thread.

        .. versionadded:: 2.0
        """
        return 32

    @flag_value
    def ephemeral(self):
        """:class:`bool`: Returns ``True`` if the message is ephemeral.

        .. versionadded:: 2.0
        """
        return 64

    @flag_value
    def loading(self):
        """:class:`bool`: Returns ``True`` if the message is an interaction response and the bot
        is "thinking".

        .. versionadded:: 2.0
        """
        return 128

    @flag_value
    def failed_to_mention_some_roles_in_thread(self):
        """:class:`bool`: Returns ``True`` if the message failed to mention some roles in a thread
        and add their members to the thread.

        .. versionadded:: 2.0
        """
        return 256

    @flag_value
    def link_not_discord_warning(self):
        """:class:`bool`: Returns ``True`` if this message contains a link that impersonates
        Discord and should show a warning.

        .. versionadded:: 2.0
        """
        return 1024

    @flag_value
    def suppress_notifications(self):
        """:class:`bool`: Returns ``True`` if the message will not trigger push and desktop notifications.

        .. versionadded:: 2.0
        """
        return 4096

    @alias_flag_value
    def silent(self):
        """:class:`bool`: Alias for :attr:`suppress_notifications`.

        .. versionadded:: 2.0
        """
        return 4096

    @flag_value
    def voice(self):
        """:class:`bool`: Returns ``True`` if the message is a voice message.

        .. versionadded:: 2.1
        """
        return 8192


@fill_with_flags()
class MemberCacheFlags(BaseFlags):
    """Controls the library's cache policy when it comes to members.

    This allows for finer grained control over what members are cached.
    Note that the bot's own member is always cached. This class is passed
    to the ``member_cache_flags`` parameter in :class:`Client`.

    To construct an object you can pass keyword arguments denoting the flags
    to enable or disable.

    The default value is all flags enabled.

    .. versionadded:: 1.5

    .. container:: operations

        .. describe:: x == y

            Checks if two flags are equal.
        .. describe:: x != y

            Checks if two flags are not equal.

        .. describe:: x | y, x |= y

            Returns a MemberCacheFlags instance with all enabled flags from
            both x and y.

            .. versionadded:: 2.0
        .. describe:: x & y, x &= y

            Returns a MemberCacheFlags instance with only flags enabled on
            both x and y.

            .. versionadded:: 2.0
        .. describe:: x ^ y, x ^= y

            Returns a MemberCacheFlags instance with only flags enabled on
            only one of x or y, not on both.

            .. versionadded:: 2.0
        .. describe:: ~x

            Returns a MemberCacheFlags instance with all flags inverted from x.

            .. versionadded:: 2.0
        .. describe:: hash(x)

               Return the flag's hash.
        .. describe:: iter(x)

               Returns an iterator of ``(name, value)`` pairs. This allows it
               to be, for example, constructed as a dict or a list of pairs.
        .. describe:: bool(b)

            Returns whether any flag is set to ``True``.

            .. versionadded:: 2.0

    Attributes
    -----------
    value: :class:`int`
        The raw value. You should query flags via the properties
        rather than using this raw value.
    """

    __slots__ = ()

    def __init__(self, **kwargs: bool):
        bits = max(self.VALID_FLAGS.values()).bit_length()
        self.value: int = (1 << bits) - 1
        for key, value in kwargs.items():
            if key not in self.VALID_FLAGS:
                raise TypeError(f"{key!r} is not a valid flag name.")
            setattr(self, key, value)

    @classmethod
    def all(cls: Type[MemberCacheFlags]) -> MemberCacheFlags:
        """A factory method that creates a :class:`MemberCacheFlags` with everything enabled."""
        bits = max(cls.VALID_FLAGS.values()).bit_length()
        value = (1 << bits) - 1
        self = cls.__new__(cls)
        self.value = value
        return self

    @classmethod
    def none(cls: Type[MemberCacheFlags]) -> MemberCacheFlags:
        """A factory method that creates a :class:`MemberCacheFlags` with everything disabled."""
        self = cls.__new__(cls)
        self.value = self.DEFAULT_VALUE
        return self

    @property
    def _empty(self):
        return self.value == self.DEFAULT_VALUE

    @flag_value
    def voice(self):
        """:class:`bool`: Whether to cache members that are in voice.

        Members that leave voice are no longer cached.
        """
        return 1

    @flag_value
    def other(self):
        """:class:`bool`: Whether to cache members that are collected from other means.

        This does not apply to members explicitly cached (e.g. :attr:`Guild.chunk`, :attr:`Guild.fetch_members`).

        There is an alias for this called :attr:`joined`.
        """
        return 2

    @alias_flag_value
    def joined(self):
        """:class:`bool`: Whether to cache members that are collected from other means.

        This does not apply to members explicitly cached (e.g. :attr:`Guild.chunk`, :attr:`Guild.fetch_members`).

        This is an alias for :attr:`other`.
        """
        return 2

    @property
    def _voice_only(self):
        return self.value == 1


@fill_with_flags()
class ApplicationFlags(BaseFlags):
    r"""Wraps up the Discord Application flags.

    .. container:: operations

        .. describe:: x == y

            Checks if two ApplicationFlags are equal.
        .. describe:: x != y

            Checks if two ApplicationFlags are not equal.
        .. describe:: x | y, x |= y

            Returns an ApplicationFlags instance with all enabled flags from
            both x and y.
        .. describe:: x & y, x &= y

            Returns an ApplicationFlags instance with only flags enabled on
            both x and y.
        .. describe:: x ^ y, x ^= y

            Returns an ApplicationFlags instance with only flags enabled on
            only one of x or y, not on both.
        .. describe:: ~x

            Returns an ApplicationFlags instance with all flags inverted from x.
        .. describe:: hash(x)

            Return the flag's hash.
        .. describe:: iter(x)

            Returns an iterator of ``(name, value)`` pairs. This allows it
            to be, for example, constructed as a dict or a list of pairs.
            Note that aliases are not shown.
        .. describe:: bool(b)

            Returns whether any flag is set to ``True``.

    .. versionadded:: 2.0

    .. versionchanged:: 2.1

        Removed now-defunct flag values.

    Attributes
    -----------
    value: :class:`int`
        The raw value. You should query flags via the properties
        rather than using this raw value.
    """

    # Commented-out flags are no longer used; they are kept here for historical purposes

    __slots__ = ()

    # @flag_value
    # def embedded_released(self):
    #     """:class:`bool`: Returns ``True`` if the embedded application is released to the public."""
    #     return 1 << 1

    @flag_value
    def managed_emoji(self):
        """:class:`bool`: Returns ``True`` if the application has the ability to create managed emoji."""
        return 1 << 2

    @flag_value
    def embedded_iap(self):
        """:class:`bool`: Returns ``True`` if the embedded application has the ability to use in-app purchases."""
        return 1 << 3

    @flag_value
    def group_dm_create(self):
        """:class:`bool`: Returns ``True`` if the application has the ability to create group DMs without limit."""
        return 1 << 4

    # @flag_value
    # def rpc_private_beta(self):
    #     """:class:`bool`: Returns ``True`` if the application has the ability to access the client RPC server."""
    #     return 1 << 5

    # @flag_value
    # def allow_assets(self):
    #     """:class:`bool`: Returns ``True`` if the application has the ability to use activity assets."""
    #     return 1 << 8

    # @flag_value
    # def allow_activity_action_spectate(self):
    #     """:class:`bool`: Returns ``True`` if the application has the ability to enable spectating activities."""
    #     return 1 << 9

    # @flag_value
    # def allow_activity_action_join_request(self):
    #     """:class:`bool`: Returns ``True`` if the application has the ability to enable activity join requests."""
    #     return 1 << 10

    # @flag_value
    # def rpc_has_connected(self):
    #     """:class:`bool`: Returns ``True`` if the application has accessed the client RPC server before."""
    #     return 1 << 11

    @flag_value
    def gateway_presence(self):
        """:class:`bool`: Returns ``True`` if the application is verified and is allowed to
        receive presence information over the gateway.
        """
        return 1 << 12

    @flag_value
    def gateway_presence_limited(self):
        """:class:`bool`: Returns ``True`` if the application is allowed to receive
        presence information over the gateway.
        """
        return 1 << 13

    @flag_value
    def gateway_guild_members(self):
        """:class:`bool`: Returns ``True`` if the application is verified and is allowed to
        receive full guild member lists.
        """
        return 1 << 14

    @flag_value
    def gateway_guild_members_limited(self):
        """:class:`bool`: Returns ``True`` if the application is allowed to receive full
        guild member lists.
        """
        return 1 << 15

    @flag_value
    def verification_pending_guild_limit(self):
        """:class:`bool`: Returns ``True`` if the application has had unusual growth,
        temporarily preventing verification.
        """
        return 1 << 16

    @flag_value
    def embedded(self):
        """:class:`bool`: Returns ``True`` if the application can be embedded within the Discord client."""
        return 1 << 17

    @flag_value
    def gateway_message_content(self):
        """:class:`bool`: Returns ``True`` if the application is verified and is allowed to
        receive message content in guilds."""
        return 1 << 18

    @flag_value
    def gateway_message_content_limited(self):
        """:class:`bool`: Returns ``True`` if the application is allowed to
        read message content in guilds."""
        return 1 << 19

    @flag_value
    def embedded_first_party(self):
        """:class:`bool`: Returns ``True`` if the embedded application is published by Discord."""
        return 1 << 20

    @flag_value
    def application_command_badge(self):
        """:class:`bool`: Returns ``True`` if the application has registered global application commands."""
        return 1 << 23

    @flag_value
    def active(self):
        """:class:`bool`: Returns ``True`` if the application is considered active.
        This means that it has had any global command executed in the past 30 days.
        """
        return 1 << 24


@fill_with_flags()
class ChannelFlags(BaseFlags):
    r"""Wraps up the Discord :class:`~discord.abc.GuildChannel` or :class:`Thread` flags.

    .. container:: operations

        .. describe:: x == y

            Checks if two ChannelFlags are equal.
        .. describe:: x | y, x |= y

            Returns a ChannelFlags instance with all enabled flags from
            both x and y.
        .. describe:: x & y, x &= y

            Returns a ChannelFlags instance with only flags enabled on
            both x and y.
        .. describe:: x ^ y, x ^= y

            Returns a ChannelFlags instance with only flags enabled on
            only one of x or y, not on both.
        .. describe:: ~x

            Returns a ChannelFlags instance with all flags inverted from x.
        .. describe:: hash(x)

            Return the flag's hash.
        .. describe:: iter(x)

            Returns an iterator of ``(name, value)`` pairs. This allows it
            to be, for example, constructed as a dict or a list of pairs.
            Note that aliases are not shown.
        .. describe:: bool(b)

            Returns whether any flag is set to ``True``.

    .. versionadded:: 2.0

    Attributes
    -----------
    value: :class:`int`
        The raw value. You should query flags via the properties
        rather than using this raw value.
    """

    __slots__ = ()

    @flag_value
    def pinned(self):
        """:class:`bool`: Returns ``True`` if the thread is pinned to the forum channel."""
        return 1 << 1

    @flag_value
    def require_tag(self):
        """:class:`bool`: Returns ``True`` if a tag is required to be specified when creating a thread in a :class:`ForumChannel`."""
        return 1 << 4


@fill_with_flags()
class PaymentSourceFlags(BaseFlags):
    r"""Wraps up the Discord payment source flags.

    .. container:: operations

        .. describe:: x == y

            Checks if two PaymentSourceFlags are equal.
        .. describe:: x != y

            Checks if two PaymentSourceFlags are not equal.
        .. describe:: x | y, x |= y

            Returns a PaymentSourceFlags instance with all enabled flags from
            both x and y.
        .. describe:: x & y, x &= y

            Returns a PaymentSourceFlags instance with only flags enabled on
            both x and y.
        .. describe:: x ^ y, x ^= y

            Returns a PaymentSourceFlags instance with only flags enabled on
            only one of x or y, not on both.
        .. describe:: ~x

            Returns a PaymentSourceFlags instance with all flags inverted from x.
        .. describe:: hash(x)

            Return the flag's hash.
        .. describe:: iter(x)

            Returns an iterator of ``(name, value)`` pairs. This allows it
            to be, for example, constructed as a dict or a list of pairs.
            Note that aliases are not shown.
        .. describe:: bool(b)

            Returns whether any flag is set to ``True``.

    .. versionadded:: 2.0

    Attributes
    -----------
    value: :class:`int`
        The raw value. This value is a bit array field of a 53-bit integer
        representing the currently available flags. You should query
        flags via the properties rather than using this raw value.
    """

    __slots__ = ()

    @flag_value
    def new(self):
        """:class:`bool`: Returns ``True`` if the payment source is new."""
        return 1 << 0

    @flag_value
    def unknown(self):
        return 1 << 1


@fill_with_flags()
class LibraryApplicationFlags(BaseFlags):
    r"""Wraps up the Discord library application flags.

    .. container:: operations

        .. describe:: x == y

            Checks if two LibraryApplicationFlags are equal.
        .. describe:: x != y

            Checks if two LibraryApplicationFlags are not equal.
        .. describe:: x | y, x |= y

            Returns a LibraryApplicationFlags instance with all enabled flags from
            both x and y.
        .. describe:: x & y, x &= y

            Returns a LibraryApplicationFlags instance with only flags enabled on
            both x and y.
        .. describe:: x ^ y, x ^= y

            Returns a LibraryApplicationFlags instance with only flags enabled on
            only one of x or y, not on both.
        .. describe:: ~x

            Returns a LibraryApplicationFlags instance with all flags inverted from x.
        .. describe:: hash(x)

            Return the flag's hash.
        .. describe:: iter(x)

            Returns an iterator of ``(name, value)`` pairs. This allows it
            to be, for example, constructed as a dict or a list of pairs.
            Note that aliases are not shown.
        .. describe:: bool(b)

            Returns whether any flag is set to ``True``.

    .. versionadded:: 2.0

    Attributes
    -----------
    value: :class:`int`
        The raw value. This value is a bit array field of a 53-bit integer
        representing the currently available flags. You should query
        flags via the properties rather than using this raw value.
    """

    __slots__ = ()

    @flag_value
    def hidden(self):
        """:class:`bool`: Returns ``True`` if the library application is hidden."""
        return 1 << 0

    @flag_value
    def private(self):
        """:class:`bool`: Returns ``True`` if the library application is not shown in playing status."""
        return 1 << 1

    @flag_value
    def overlay_disabled(self):
        """:class:`bool`: Returns ``True`` if the library application has the Discord overlay disabled."""
        return 1 << 2

    @flag_value
    def entitled(self):
        """:class:`bool`: Returns ``True`` if the library application is entitled to the user."""
        return 1 << 3


@fill_with_flags()
class ApplicationDiscoveryFlags(BaseFlags):
    r"""Wraps up the Discord application discovery eligibility flags.

    .. container:: operations

        .. describe:: x == y

            Checks if two ApplicationDiscoveryFlags are equal.
        .. describe:: x != y

            Checks if two ApplicationDiscoveryFlags are not equal.
        .. describe:: x | y, x |= y

            Returns a ApplicationDiscoveryFlags instance with all enabled flags from
            both x and y.
        .. describe:: x & y, x &= y

            Returns a ApplicationDiscoveryFlags instance with only flags enabled on
            both x and y.
        .. describe:: x ^ y, x ^= y

            Returns a ApplicationDiscoveryFlags instance with only flags enabled on
            only one of x or y, not on both.
        .. describe:: ~x

            Returns a ApplicationDiscoveryFlags instance with all flags inverted from x.
        .. describe:: hash(x)

            Return the flag's hash.
        .. describe:: iter(x)

            Returns an iterator of ``(name, value)`` pairs. This allows it
            to be, for example, constructed as a dict or a list of pairs.
            Note that aliases are not shown.
        .. describe:: bool(b)

            Returns whether any flag is set to ``True``.

    .. versionadded:: 2.0

    Attributes
    -----------
    value: :class:`int`
        The raw value. This value is a bit array field of a 53-bit integer
        representing the currently available flags. You should query
        flags via the properties rather than using this raw value.
    """

    __slots__ = ()

    @flag_value
    def verified(self):
        """:class:`bool`: Returns ``True`` if the application is verified."""
        return 1 << 0

    @flag_value
    def tag(self):
        """:class:`bool`: Returns ``True`` if the application has at least one tag set."""
        return 1 << 1

    @flag_value
    def description(self):
        """:class:`bool`: Returns ``True`` if the application has a description."""
        return 1 << 2

    @flag_value
    def terms_of_service(self):
        """:class:`bool`: Returns ``True`` if the application has a terms of service."""
        return 1 << 3

    @flag_value
    def privacy_policy(self):
        """:class:`bool`: Returns ``True`` if the application has a privacy policy."""
        return 1 << 4

    @flag_value
    def install_params(self):
        """:class:`bool`: Returns ``True`` if the application has a custom install URL or install parameters."""
        return 1 << 5

    @flag_value
    def safe_name(self):
        """:class:`bool`: Returns ``True`` if the application name is safe for work."""
        return 1 << 6

    @flag_value
    def safe_description(self):
        """:class:`bool`: Returns ``True`` if the application description is safe for work."""
        return 1 << 7

    @flag_value
    def approved_commands(self):
        """:class:`bool`: Returns ``True`` if the application has the message content intent approved or utilizes application commands."""
        return 1 << 8

    @flag_value
    def support_guild(self):
        """:class:`bool`: Returns ``True`` if the application has a support guild set."""
        return 1 << 9

    @flag_value
    def safe_commands(self):
        """:class:`bool`: Returns ``True`` if the application's commands are safe for work."""
        return 1 << 10

    @flag_value
    def mfa(self):
        """:class:`bool`: Returns ``True`` if the application's owner has MFA enabled."""
        return 1 << 11

    @flag_value
    def safe_directory_overview(self):
        """:class:`bool`: Returns ``True`` if the application's directory long description is safe for work."""
        return 1 << 12

    @flag_value
    def supported_locales(self):
        """:class:`bool`: Returns ``True`` if the application has at least one supported locale set."""
        return 1 << 13

    @flag_value
    def safe_short_description(self):
        """:class:`bool`: Returns ``True`` if the application's directory short description is safe for work."""
        return 1 << 14

    @flag_value
    def safe_role_connections(self):
        """:class:`bool`: Returns ``True`` if the application's role connections metadata is safe for work."""
        return 1 << 15

    @flag_value
    def eligible(self):
        """:class:`bool`: Returns ``True`` if the application has met all the above criteria and is eligible for discovery."""
        return 1 << 16


@fill_with_flags()
class FriendSourceFlags(BaseFlags):
    r"""Wraps up the Discord friend source flags.

    These are used in user settings to control who can add you as a friend.

    .. container:: operations

        .. describe:: x == y

            Checks if two FriendSourceFlags are equal.
        .. describe:: x != y

            Checks if two FriendSourceFlags are not equal.
        .. describe:: x | y, x |= y

            Returns a FriendSourceFlags instance with all enabled flags from
            both x and y.
        .. describe:: x & y, x &= y

            Returns a FriendSourceFlags instance with only flags enabled on
            both x and y.
        .. describe:: x ^ y, x ^= y

            Returns a FriendSourceFlags instance with only flags enabled on
            only one of x or y, not on both.
        .. describe:: ~x

            Returns a FriendSourceFlags instance with all flags inverted from x.
        .. describe:: hash(x)

            Return the flag's hash.
        .. describe:: iter(x)

            Returns an iterator of ``(name, value)`` pairs. This allows it
            to be, for example, constructed as a dict or a list of pairs.
            Note that aliases are not shown.
        .. describe:: bool(b)

            Returns whether any flag is set to ``True``.

    .. versionadded:: 2.0

    Attributes
    -----------
    value: :class:`int`
        The raw value. This value is a bit array field of a 53-bit integer
        representing the currently available flags. You should query
        flags via the properties rather than using this raw value.
    """

    __slots__ = ()

    @classmethod
    def _from_dict(cls, data: dict) -> Self:
        self = cls()
        if data.get("mutual_friends"):
            self.mutual_friends = True
        if data.get("mutual_guilds"):
            self.mutual_guilds = True
        if data.get("all"):
            self.no_relation = True
        return self

    def _to_dict(self) -> dict:
        return {
            "mutual_friends": self.mutual_friends,
            "mutual_guilds": self.mutual_guilds,
            "all": self.no_relation,
        }

    @classmethod
    def none(cls) -> Self:
        """A factory method that creates a :class:`FriendSourceFlags` that allows no friend request."""
        return cls()

    @classmethod
    def all(cls) -> Self:
        """A factory method that creates a :class:`FriendSourceFlags` that allows any friend requests."""
        self = cls()
        self.no_relation = True
        return self

    @flag_value
    def mutual_friends(self):
        """:class:`bool`: Returns ``True`` if a user can add you as a friend if you have mutual friends."""
        return 1 << 1

    @flag_value
    def mutual_guilds(self):
        """:class:`bool`: Returns ``True`` if a user can add you as a friend if you are in the same guild."""
        return 1 << 2

    @flag_value
    def no_relation(self):
        """:class:`bool`: Returns ``True`` if a user can always add you as a friend."""
        # Requires all of the above
        return 1 << 3 | 1 << 2 | 1 << 1


@fill_with_flags()
class FriendDiscoveryFlags(BaseFlags):
    r"""Wraps up the Discord friend discovery flags.

    These are used in user settings to control how you get recommended friends.

    .. container:: operations

        .. describe:: x == y

            Checks if two FriendDiscoveryFlags are equal.
        .. describe:: x != y

            Checks if two FriendDiscoveryFlags are not equal.
        .. describe:: x | y, x |= y

            Returns a FriendDiscoveryFlags instance with all enabled flags from
            both x and y.
        .. describe:: x & y, x &= y

            Returns a FriendDiscoveryFlags instance with only flags enabled on
            both x and y.
        .. describe:: x ^ y, x ^= y

            Returns a FriendDiscoveryFlags instance with only flags enabled on
            only one of x or y, not on both.
        .. describe:: ~x

            Returns a FriendDiscoveryFlags instance with all flags inverted from x.
        .. describe:: hash(x)

            Return the flag's hash.
        .. describe:: iter(x)

            Returns an iterator of ``(name, value)`` pairs. This allows it
            to be, for example, constructed as a dict or a list of pairs.
            Note that aliases are not shown.
        .. describe:: bool(b)

            Returns whether any flag is set to ``True``.

    .. versionadded:: 2.0

    Attributes
    -----------
    value: :class:`int`
        The raw value. This value is a bit array field of a 53-bit integer
        representing the currently available flags. You should query
        flags via the properties rather than using this raw value.
    """

    __slots__ = ()

    @classmethod
    def none(cls) -> Self:
        """A factory method that creates a :class:`FriendDiscoveryFlags` that allows no friend discovery."""
        return cls()

    @classmethod
    def all(cls) -> Self:
        """A factory method that creates a :class:`FriendDiscoveryFlags` that allows all friend discovery."""
        self = cls()
        self.find_by_email = True
        self.find_by_phone = True
        return self

    @flag_value
    def find_by_phone(self):
        """:class:`bool`: Returns ``True`` if a user can add you as a friend if they have your phone number."""
        return 1 << 1

    @flag_value
    def find_by_email(self):
        """:class:`bool`: Returns ``True`` if a user can add you as a friend if they have your email address."""
        return 1 << 2


@fill_with_flags()
class OnboardingProgressFlags(BaseFlags):
    """Wraps up the Discord guild onboarding progress flags.

    These are used in user settings, specifically guild progress, to track engagement and feature usage in guild onboarding.

    .. container:: operations

        .. describe:: x == y

            Checks if two OnboardingProgressFlags are equal.
        .. describe:: x != y

            Checks if two OnboardingProgressFlags are not equal.
        .. describe:: x | y, x |= y

            Returns a OnboardingProgressFlags instance with all enabled flags from
            both x and y.
        .. describe:: x & y, x &= y

            Returns a OnboardingProgressFlags instance with only flags enabled on
            both x and y.
        .. describe:: x ^ y, x ^= y

            Returns a OnboardingProgressFlags instance with only flags enabled on
            only one of x or y, not on both.
        .. describe:: ~x

            Returns a OnboardingProgressFlags instance with all flags inverted from x.
        .. describe:: hash(x)

            Return the flag's hash.
        .. describe:: iter(x)

            Returns an iterator of ``(name, value)`` pairs. This allows it
            to be, for example, constructed as a dict or a list of pairs.
            Note that aliases are not shown.
        .. describe:: bool(b)

            Returns whether any flag is set to ``True``.

    .. versionadded:: 2.0

    Attributes
    -----------
    value: :class:`int`
        The raw value. This value is a bit array field of a 53-bit integer
        representing the currently available flags. You should query
        flags via the properties rather than using this raw value.
    """

    __slots__ = ()

    @flag_value
    def notice_shown(self):
        """:class:`bool`: Returns ``True`` if the user has been shown the onboarding notice."""
        return 1 << 0

    @flag_value
    def notice_cleared(self):
        """:class:`bool`: Returns ``True`` if the user has cleared the onboarding notice."""
        return 1 << 1


@fill_with_flags()
class MemberFlags(BaseFlags):
    r"""Wraps up the Discord Guild Member flags

    .. container:: operations

        .. describe:: x == y

            Checks if two MemberFlags are equal.
        .. describe:: x != y

            Checks if two MemberFlags are not equal.
        .. describe:: x | y, x |= y

            Returns a MemberFlags instance with all enabled flags from
            both x and y.
        .. describe:: x & y, x &= y

            Returns a MemberFlags instance with only flags enabled on
            both x and y.
        .. describe:: x ^ y, x ^= y

            Returns a MemberFlags instance with only flags enabled on
            only one of x or y, not on both.
        .. describe:: ~x

            Returns a MemberFlags instance with all flags inverted from x.
        .. describe:: hash(x)

            Return the flag's hash.
        .. describe:: iter(x)

            Returns an iterator of ``(name, value)`` pairs. This allows it
            to be, for example, constructed as a dict or a list of pairs.
            Note that aliases are not shown.
        .. describe:: bool(b)

            Returns whether any flag is set to ``True``.

    .. versionadded:: 2.0

    Attributes
    -----------
    value: :class:`int`
        The raw value. You should query flags via the properties
        rather than using this raw value.
    """

    __slots__ = ()

    @flag_value
    def did_rejoin(self):
        """:class:`bool`: Returns ``True`` if the member left and rejoined the :attr:`~discord.Member.guild`."""
        return 1 << 0

    @flag_value
    def completed_onboarding(self):
        """:class:`bool`: Returns ``True`` if the member has completed onboarding."""
        return 1 << 1

    @flag_value
    def bypasses_verification(self):
        """:class:`bool`: Returns ``True`` if the member can bypass the guild verification requirements."""
        return 1 << 2

    @flag_value
    def started_onboarding(self):
        """:class:`bool`: Returns ``True`` if the member has started onboarding."""
        return 1 << 3

    @flag_value
    def guest(self):
        """:class:`bool`: Returns ``True`` if the member is a guest.
        Guest members are members that joined through a guest invite, and are not full members of the guild.

        .. versionadded:: 2.1
        """
        return 1 << 4


@fill_with_flags()
class ReadStateFlags(BaseFlags):
    r"""Wraps up the Discord read state flags.

    .. container:: operations

        .. describe:: x == y

            Checks if two ReadStateFlags are equal.
        .. describe:: x != y

            Checks if two ReadStateFlags are not equal.
        .. describe:: x | y, x |= y

            Returns a ReadStateFlags instance with all enabled flags from
            both x and y.
        .. describe:: x & y, x &= y

            Returns a ReadStateFlags instance with only flags enabled on
            both x and y.
        .. describe:: x ^ y, x ^= y

            Returns a ReadStateFlags instance with only flags enabled on
            only one of x or y, not on both.
        .. describe:: ~x

            Returns a ReadStateFlags instance with all flags inverted from x.
        .. describe:: hash(x)

            Return the flag's hash.
        .. describe:: iter(x)

            Returns an iterator of ``(name, value)`` pairs. This allows it
            to be, for example, constructed as a dict or a list of pairs.
            Note that aliases are not shown.
        .. describe:: bool(b)

            Returns whether any flag is set to ``True``.

    .. versionadded:: 2.1

    Attributes
    -----------
    value: :class:`int`
        The raw value. You should query flags via the properties
        rather than using this raw value.
    """

    __slots__ = ()

    @flag_value
    def guild_channel(self):
        """:class:`bool`: Returns ``True`` if the read state is for a guild channel."""
        return 1 << 0

    @flag_value
    def thread(self):
        """:class:`bool`: Returns ``True`` if the read state is for a thread."""
        return 1 << 1


@fill_with_flags()
class InviteFlags(BaseFlags):
    r"""Wraps up the Discord invite flags.

    .. container:: operations

        .. describe:: x == y

            Checks if two InviteFlags are equal.
        .. describe:: x != y

            Checks if two InviteFlags are not equal.
        .. describe:: x | y, x |= y

            Returns a InviteFlags instance with all enabled flags from
            both x and y.
        .. describe:: x & y, x &= y

            Returns a InviteFlags instance with only flags enabled on
            both x and y.
        .. describe:: x ^ y, x ^= y

            Returns a InviteFlags instance with only flags enabled on
            only one of x or y, not on both.
        .. describe:: ~x

            Returns a InviteFlags instance with all flags inverted from x.
        .. describe:: hash(x)

            Return the flag's hash.
        .. describe:: iter(x)

            Returns an iterator of ``(name, value)`` pairs. This allows it
            to be, for example, constructed as a dict or a list of pairs.
            Note that aliases are not shown.
        .. describe:: bool(b)

            Returns whether any flag is set to ``True``.

    .. versionadded:: 2.1

    Attributes
    -----------
    value: :class:`int`
        The raw value. You should query flags via the properties
        rather than using this raw value.
    """

    __slots__ = ()

    @flag_value
    def guest(self):
        """:class:`bool`: Returns ``True`` if the invite is a guest invite. Guest invites grant temporary membership for the purposes of joining a voice channel."""
        return 1 << 0


@fill_with_flags()
class AttachmentFlags(BaseFlags):
    r"""Wraps up the Discord Attachment flags

    .. container:: operations

        .. describe:: x == y

            Checks if two AttachmentFlags are equal.
        .. describe:: x != y

            Checks if two AttachmentFlags are not equal.
        .. describe:: x | y, x |= y

            Returns a AttachmentFlags instance with all enabled flags from
            both x and y.
        .. describe:: x & y, x &= y

            Returns a AttachmentFlags instance with only flags enabled on
            both x and y.
        .. describe:: x ^ y, x ^= y

            Returns a AttachmentFlags instance with only flags enabled on
            only one of x or y, not on both.
        .. describe:: ~x

            Returns a AttachmentFlags instance with all flags inverted from x.
        .. describe:: hash(x)

            Return the flag's hash.
        .. describe:: iter(x)

            Returns an iterator of ``(name, value)`` pairs. This allows it
            to be, for example, constructed as a dict or a list of pairs.
            Note that aliases are not shown.
        .. describe:: bool(b)

            Returns whether any flag is set to ``True``.

    .. versionadded:: 2.1

    Attributes
    -----------
    value: :class:`int`
        The raw value. You should query flags via the properties
        rather than using this raw value.
    """

    @flag_value
    def clip(self):
        """:class:`bool`: Returns ``True`` if the attachment is a clip."""
        return 1 << 0

    @flag_value
    def thumbnail(self):
        """:class:`bool`: Returns ``True`` if the attachment is a media channel thumbnail."""
        return 1 << 1

    @flag_value
    def remix(self):
        """:class:`bool`: Returns ``True`` if the attachment has been edited using the remix feature."""
        return 1 << 2
