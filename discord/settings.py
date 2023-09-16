"""
The MIT License (MIT)

Copyright (c) 2021-present Dolfies

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

import base64
import logging
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Literal,
    Optional,
    Type,
    Union,
    overload,
)

from discord_protos import PreloadedUserSettings  # , FrecencyUserSettings
from google.protobuf.json_format import MessageToDict, ParseDict

from .activity import CustomActivity
from .enums import (
    Status,
    try_enum,
)
from .object import Object
from .utils import (
    MISSING,
    _ocast,
)

if TYPE_CHECKING:
    from google.protobuf.message import Message
    from typing_extensions import Self

    from .channel import DMChannel, GroupChannel
    from .guild import Guild
    from .state import ConnectionState

    PrivateChannel = Union[DMChannel, GroupChannel]

__all__ = ("UserSettings",)

_log = logging.getLogger(__name__)


class _ProtoSettings:
    __slots__ = (
        "_state",
        "settings",
    )

    PROTOBUF_CLS: Type[Message] = MISSING
    settings: Any

    # I honestly wish I didn't have to vomit properties everywhere like this,
    # but unfortunately it's probably the best way to do it
    # The discord-protos library is maintained seperately, so any changes
    # to the protobufs will have to be reflected here;
    # this is why I'm keeping the `settings` attribute public
    # I love protobufs :blobcatcozystars:

    def __init__(self, state: ConnectionState, data: str):
        self._state: ConnectionState = state
        self._update(data)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.settings == other.settings
        return False

    def __ne__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.settings != other.settings
        return True

    def _update(self, data: str, *, partial: bool = False):
        if partial:
            self.merge_from_base64(data)
        else:
            self.from_base64(data)

    @classmethod
    def _copy(cls, self: Self, /) -> Self:
        new = cls.__new__(cls)
        new._state = self._state
        new.settings = cls.PROTOBUF_CLS()
        new.settings.CopyFrom(self.settings)
        return new

    @overload
    def _get_guild(self, id: int, /, *, always_guild: Literal[True] = ...) -> Guild: ...

    @overload
    def _get_guild(
        self, id: int, /, *, always_guild: Literal[False] = ...
    ) -> Union[Guild, Object]: ...

    def _get_guild(
        self, id: int, /, *, always_guild: bool = False
    ) -> Union[Guild, Object]:
        id = int(id)
        if always_guild:
            return self._state._get_or_create_unavailable_guild(id)
        return self._state._get_guild(id) or Object(id=id)

    def to_dict(self, *, with_defaults: bool = False) -> Dict[str, Any]:
        return MessageToDict(
            self.settings,
            including_default_value_fields=with_defaults,
            preserving_proto_field_name=True,
            use_integers_for_enums=True,
        )

    def dict_to_base64(self, data: Dict[str, Any]) -> str:
        message = ParseDict(data, self.PROTOBUF_CLS())
        return base64.b64encode(message.SerializeToString()).decode("ascii")

    def from_base64(self, data: str):
        self.settings = self.PROTOBUF_CLS().FromString(base64.b64decode(data))

    def merge_from_base64(self, data: str):
        self.settings.MergeFromString(base64.b64decode(data))

    def to_base64(self) -> str:
        return base64.b64encode(self.settings.SerializeToString()).decode("ascii")


class UserSettings(_ProtoSettings):
    """Represents the Discord client settings.

    .. versionadded:: 2.0
    """

    __slots__ = ()

    PROTOBUF_CLS = PreloadedUserSettings

    # Client versions are supposed to be backwards compatible
    # If the client supports a version newer than the one in data,
    # it does a migration and updates the version in data
    SUPPORTED_CLIENT_VERSION = 17
    SUPPORTED_SERVER_VERSION = 0

    def __init__(self, *args):
        super().__init__(*args)
        if self.client_version < self.SUPPORTED_CLIENT_VERSION:
            # Migrations are mostly for client state, but we'll throw a debug log anyway
            _log.debug(
                "PreloadedUserSettings client version is outdated, migration needed."
                " Unexpected behaviour may occur."
            )
        if self.server_version > self.SUPPORTED_SERVER_VERSION:
            # At the time of writing, the server version is not provided (so it's always 0)
            # The client does not use the field at all, so there probably won't be any server-side migrations anytime soon
            _log.debug(
                "PreloadedUserSettings server version is newer than supported."
                " Unexpected behaviour may occur."
            )

    @property
    def data_version(self) -> int:
        """:class:`int`: The version of the settings. Increases on every change."""
        return self.settings.versions.data_version

    @property
    def client_version(self) -> int:
        """:class:`int`: The client version of the settings. Used for client-side data migrations."""
        return self.settings.versions.client_version

    @property
    def server_version(self) -> int:
        """:class:`int`: The server version of the settings. Used for server-side data migrations."""
        return self.settings.versions.server_version

    # Status Settings

    @property
    def status(self) -> Status:
        """:class:`Status`: The configured status."""
        return try_enum(Status, self.settings.status.status.value or "unknown")

    @property
    def custom_activity(self) -> Optional[CustomActivity]:
        """:class:`CustomActivity`: The set custom activity."""
        return (
            CustomActivity._from_settings(
                data=self.settings.status.custom_status, state=self._state
            )
            if self.settings.status.HasField("custom_status")
            else None
        )

    @property
    def show_current_game(self) -> bool:
        """:class:`bool`: Whether to show the current game."""
        return (
            self.settings.status.show_current_game.value
            if self.settings.status.HasField("show_current_game")
            else True
        )

    @overload
    async def edit(self) -> Self: ...

    @overload
    async def edit(
        self,
        *,
        require_version: Union[bool, int] = False,
        client_version: int = ...,
        status: Status = ...,
        custom_activity: Optional[CustomActivity] = ...,
        show_current_game: bool = (...,),
    ) -> Self: ...

    async def edit(
        self, *, require_version: Union[bool, int] = False, **kwargs: Any
    ) -> Self:
        r"""|coro|

        Edits the current user's settings.

        .. note::

            Settings subsections are not idempotently updated. This means if you change one setting in a subsection\* on an outdated
            instance of :class:`UserSettings` then the other settings in that subsection\* will be reset to the value of the instance.

            When operating on the cached user settings (i.e. :attr:`Client.settings`), this should not be an issue. However, if you
            are operating on a fetched instance, consider using the ``require_version`` parameter to ensure you don't overwrite
            newer settings.

            Any field may be explicitly set to ``MISSING`` to reset it to the default value.

            \* A subsection is a group of settings that are stored in the same top-level protobuf message.
            Examples include Privacy, Text and Images, Voice and Video, etc.

        .. note::

            This method is ratelimited heavily. Updates should be batched together and sent at intervals.

            Infrequent actions do not need a delay. Frequent actions should be delayed by 10 seconds and batched.
            Automated actions (such as migrations or frecency updates) should be delayed by 30 seconds and batched.
            Daily actions (things that change often and are not meaningful, such as emoji frencency) should be delayed by 1 day and batched.

        Parameters
        ----------
        require_version: Union[:class:`bool`, :class:`int`]
            Whether to require the current version of the settings to be the same as the provided version.
            If this is ``True`` then the current version is used.
        \*\*kwargs
            The settings to edit. Refer to the :class:`UserSettings` properties for the valid fields. Unknown fields are ignored.

        Raises
        ------
        HTTPException
            Editing the settings failed.
        TypeError
            At least one setting is required to edit.

        Returns
        -------
        :class:`UserSettings`
            The edited settings. Note that this is a new instance and not the same as the cached instance as mentioned above.
        """
        # As noted above, entire sections MUST be sent, or they will be reset to default values
        # Conversely, we want to omit fields that the user requests to be set to default (by explicitly passing MISSING)
        # For this, we then remove fields set to MISSING from the payload in the payload construction at the end

        if not kwargs:
            raise TypeError("edit() missing at least 1 required keyword-only argument")

        # Only client_version should ever really be sent
        versions = {}
        for field in ("data_version", "client_version", "server_version"):
            if field in kwargs:
                versions[field] = kwargs.pop(field)

        status = {}
        if "status" in kwargs:
            status["status"] = _ocast(kwargs.pop("status"), str)
        if "custom_activity" in kwargs:
            status["custom_status"] = (
                kwargs.pop("custom_activity").to_settings_dict()
                if kwargs["custom_activity"] not in {MISSING, None}
                else MISSING
            )
        for field in ("show_current_game",):
            if field in kwargs:
                status[field] = kwargs.pop(field)

        # Now, we do the actual patching
        existing = self.to_dict()
        payload = {}
        for subsetting in (
            "versions",
            "status",
        ):
            subsetting_dict = locals()[subsetting]
            if subsetting_dict:
                original = existing.get(subsetting, {})
                original.update(subsetting_dict)
                for k, v in dict(original).items():
                    if v is MISSING:
                        del original[k]
                payload[subsetting] = original

        state = self._state
        require_version = (
            self.data_version if require_version == True else require_version
        )
        ret = await state.http.edit_proto_settings(
            1, self.dict_to_base64(payload), require_version or None
        )
        return UserSettings(state, ret["settings"])
