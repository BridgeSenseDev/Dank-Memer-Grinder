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

from typing import Any, Optional, Tuple, TYPE_CHECKING, Union

import discord.abc
from .asset import Asset

if TYPE_CHECKING:
    from typing_extensions import Self

    from .channel import DMChannel
    from .state import ConnectionState
    from .types.channel import DMChannel as DMChannelPayload
    from .types.user import (
        PartialUser as PartialUserPayload,
        User as UserPayload,
    )


__all__ = (
    "User",
    "ClientUser",
)


class _UserTag:
    __slots__ = ()
    id: int


class BaseUser(_UserTag):
    __slots__ = (
        "name",
        "id",
        "discriminator",
        "global_name",
        "_avatar",
        "bot",
        "system",
        "_state",
    )

    if TYPE_CHECKING:
        name: str
        id: int
        discriminator: str
        global_name: Optional[str]
        bot: bool
        system: bool
        _state: ConnectionState
        _avatar: Optional[str]

    def __init__(
        self, *, state: ConnectionState, data: Union[UserPayload, PartialUserPayload]
    ) -> None:
        self._state = state
        self._update(data)

    def __repr__(self) -> str:
        return (
            "<BaseUser"
            f" id={self.id} name={self.name!r} global_name={self.global_name!r}"
            f" bot={self.bot} system={self.system}>"
        )

    def __str__(self) -> str:
        if self.discriminator == "0":
            return self.name
        return f"{self.name}#{self.discriminator}"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _UserTag) and other.id == self.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return self.id >> 22

    def _update(self, data: Union[UserPayload, PartialUserPayload]) -> None:
        self.name = data["username"]
        self.id = int(data["id"])
        self.discriminator = data["discriminator"]
        self.global_name = data.get("global_name")
        self._avatar = data["avatar"]
        self.bot = data.get("bot", False)
        self.system = data.get("system", False)

    @classmethod
    def _copy(cls, user: Self) -> Self:
        self = cls.__new__(cls)  # bypass __init__

        self.name = user.name
        self.id = user.id
        self.discriminator = user.discriminator
        self.global_name = user.global_name
        self._avatar = user._avatar
        self.bot = user.bot
        self.system = user.system
        self._state = user._state

        return self

    @property
    def avatar(self) -> Optional[Asset]:
        """Optional[:class:`Asset`]: Returns an :class:`Asset` for the avatar the user has.

        If the user has not uploaded a global avatar, ``None`` is returned.
        If you want the avatar that a user has displayed, consider :attr:`display_avatar`.
        """
        if self._avatar is not None:
            return Asset._from_avatar(self._state, self.id, self._avatar)
        return None

    @property
    def default_avatar(self) -> Asset:
        """:class:`Asset`: Returns the default avatar for a given user."""
        if self.discriminator == "0":
            avatar_id = (self.id >> 22) % 6
        else:
            avatar_id = int(self.discriminator) % 5

        return Asset._from_default_avatar(self._state, avatar_id)

    @property
    def display_avatar(self) -> Asset:
        """:class:`Asset`: Returns the user's display avatar.

        For regular users this is just their default avatar or uploaded avatar.

        .. versionadded:: 2.0
        """
        return self.avatar or self.default_avatar

    @property
    def display_name(self) -> str:
        """:class:`str`: Returns the user's display name.

        For regular users this is just their global name or their username,
        but if they have a guild specific nickname then that
        is returned instead.
        """
        if self.global_name:
            return self.global_name
        return self.name

    def is_pomelo(self) -> bool:
        """:class:`bool`: Checks if the user has migrated to Discord's `new unique username system <https://discord.com/blog/usernames>`_

        .. versionadded:: 2.1
        """
        return self.discriminator == "0"


class ClientUser(BaseUser):
    """Represents your Discord user.

    .. container:: operations

        .. describe:: x == y

            Checks if two users are equal.

        .. describe:: x != y

            Checks if two users are not equal.

        .. describe:: hash(x)

            Return the user's hash.

        .. describe:: str(x)

            Returns the user's handle (e.g. ``name`` or ``name#discriminator``).

    .. versionchanged:: 2.0
        :attr:`Locale` is now a :class:`Locale` instead of a Optional[:class:`str`].

    Attributes
    -----------
    name: :class:`str`
        The user's username.
    id: :class:`int`
        The user's unique ID.
    discriminator: :class:`str`
        The user's discriminator. This is a legacy concept that is no longer used.
    global_name: Optional[:class:`str`]
        The user's global nickname, taking precedence over the username in display.

        .. versionadded:: 2.1
    bot: :class:`bool`
        Specifies if the user is a bot account.
    system: :class:`bool`
        Specifies if the user is a system user (i.e. represents Discord officially).

        .. versionadded:: 1.3
    """

    __slots__ = (
        "__weakref__",
        "_flags",
    )

    if TYPE_CHECKING:
        _flags: int

    def __init__(self, *, state: ConnectionState, data: UserPayload) -> None:
        self._state = state
        self._full_update(data)

    def __repr__(self) -> str:
        return (
            "<ClientUser"
            f" id={self.id} name={self.name!r} global_name={self.global_name!r}>"
        )

    def _full_update(self, data: UserPayload) -> None:
        self._update(data)
        self._flags = data.get("flags", 0)

    def _update_self(self, *args: Any) -> None:
        # ClientUser is kept up to date by USER_UPDATEs only
        return


class User(BaseUser, discord.abc.Connectable, discord.abc.Messageable):
    """Represents a Discord user.

    .. container:: operations

        .. describe:: x == y

            Checks if two users are equal.

        .. describe:: x != y

            Checks if two users are not equal.

        .. describe:: hash(x)

            Return the user's hash.

        .. describe:: str(x)

            Returns the user's handle (e.g. ``name`` or ``name#discriminator``).

    Attributes
    -----------
    name: :class:`str`
        The user's username.
    id: :class:`int`
        The user's unique ID.
    discriminator: :class:`str`
        The user's discriminator. This is a legacy concept that is no longer used.
    global_name: Optional[:class:`str`]
        The user's global nickname, taking precedence over the username in display.

        .. versionadded:: 2.1
    bot: :class:`bool`
        Specifies if the user is a bot account.
    system: :class:`bool`
        Specifies if the user is a system user (i.e. represents Discord officially).
    """

    __slots__ = ("__weakref__",)

    def __repr__(self) -> str:
        return (
            "<User"
            f" id={self.id} name={self.name!r} global_name={self.global_name!r} bot={self.bot}>"
        )

    def _update_self(
        self, user: Union[PartialUserPayload, Tuple[()]]
    ) -> Optional[Tuple[User, User]]:
        if len(user) == 0 or len(user) <= 1:  # Done because of typing
            return

        original = (
            self.name,
            self._avatar,
            self.discriminator,
        )
        # These keys seem to always be available
        modified = (
            user["username"],
            user.get("avatar"),
            user["discriminator"],
            user.get("global_name"),
        )
        if original != modified:
            to_return = User._copy(self)
            (
                self.name,
                self._avatar,
                self.discriminator,
                self.global_name,
            ) = modified
            # Signal to dispatch user_update
            return to_return, self

    async def _get_channel(self) -> DMChannel:
        ch = await self.create_dm()
        return ch

    @property
    def dm_channel(self) -> Optional[DMChannel]:
        """Optional[:class:`DMChannel`]: Returns the channel associated with this user if it exists.

        If this returns ``None``, you can create a DM channel by calling the
        :meth:`create_dm` coroutine function.
        """
        return self._state._get_private_channel_by_user(self.id)

    async def create_dm(self) -> DMChannel:
        """|coro|

        Creates a :class:`DMChannel` with this user.

        This should be rarely called, as this is done transparently for most
        people.

        Returns
        -------
        :class:`.DMChannel`
            The channel that was created.
        """
        found = self.dm_channel
        if found is not None:
            return found

        state = self._state
        data: DMChannelPayload = await state.http.start_private_message(self.id)
        return state.add_dm_channel(data)
