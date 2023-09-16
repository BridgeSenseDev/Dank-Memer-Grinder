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

import types
from collections import namedtuple
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Iterator,
    List,
    Mapping,
    Tuple,
    Type,
    TypeVar,
)

__all__ = (
    "Enum",
    "ChannelType",
    "MessageType",
    "Status",
    "ActivityType",
    "ExpireBehaviour",
    "ExpireBehavior",
    "ComponentType",
    "ButtonStyle",
    "TextStyle",
    "InteractionType",
    "EntityType",
    "ApplicationCommandType",
    "AppCommandType",
    "ApplicationCommandOptionType",
    "AppCommandOptionType",
    "ClientType",
    "OperatingSystem",
    "ReadStateType",
    "try_enum",
)

if TYPE_CHECKING:
    from typing_extensions import Self


def _create_value_cls(name: str, comparable: bool):
    # All the type ignores here are due to the type checker being unable to recognise
    # Runtime type creation without exploding.
    cls = namedtuple("_EnumValue_" + name, "name value")
    cls.__repr__ = lambda self: f"<{name}.{self.name}: {self.value!r}>"  # type: ignore
    cls.__str__ = lambda self: f"{name}.{self.name}"  # type: ignore
    if comparable:
        cls.__le__ = lambda self, other: isinstance(other, self.__class__) and self.value <= other.value  # type: ignore
        cls.__ge__ = lambda self, other: isinstance(other, self.__class__) and self.value >= other.value  # type: ignore
        cls.__lt__ = lambda self, other: isinstance(other, self.__class__) and self.value < other.value  # type: ignore
        cls.__gt__ = lambda self, other: isinstance(other, self.__class__) and self.value > other.value  # type: ignore
    return cls


def _is_descriptor(obj):
    return (
        hasattr(obj, "__get__") or hasattr(obj, "__set__") or hasattr(obj, "__delete__")
    )


class EnumMeta(type):
    if TYPE_CHECKING:
        __name__: ClassVar[str]
        _enum_member_names_: ClassVar[List[str]]
        _enum_member_map_: ClassVar[Dict[str, Any]]
        _enum_value_map_: ClassVar[Dict[Any, Any]]

    def __new__(
        cls,
        name: str,
        bases: Tuple[type, ...],
        attrs: Dict[str, Any],
        *,
        comparable: bool = False,
    ) -> Self:
        value_mapping = {}
        member_mapping = {}
        member_names = []

        value_cls = _create_value_cls(name, comparable)
        for key, value in list(attrs.items()):
            is_descriptor = _is_descriptor(value)
            if key[0] == "_" and not is_descriptor:
                continue

            # Special case classmethod to just pass through
            if isinstance(value, classmethod):
                continue

            if is_descriptor:
                setattr(value_cls, key, value)
                del attrs[key]
                continue

            try:
                new_value = value_mapping[value]
            except KeyError:
                new_value = value_cls(name=key, value=value)
                value_mapping[value] = new_value
                member_names.append(key)

            member_mapping[key] = new_value
            attrs[key] = new_value

        attrs["_enum_value_map_"] = value_mapping
        attrs["_enum_member_map_"] = member_mapping
        attrs["_enum_member_names_"] = member_names
        attrs["_enum_value_cls_"] = value_cls
        actual_cls = super().__new__(cls, name, bases, attrs)
        value_cls._actual_enum_cls_ = actual_cls  # type: ignore # Runtime attribute isn't understood
        return actual_cls

    def __iter__(cls) -> Iterator[Any]:
        return (cls._enum_member_map_[name] for name in cls._enum_member_names_)

    def __reversed__(cls) -> Iterator[Any]:
        return (
            cls._enum_member_map_[name] for name in reversed(cls._enum_member_names_)
        )

    def __len__(cls) -> int:
        return len(cls._enum_member_names_)

    def __repr__(cls) -> str:
        return f"<enum {cls.__name__}>"

    @property
    def __members__(cls) -> Mapping[str, Any]:
        return types.MappingProxyType(cls._enum_member_map_)

    def __call__(cls, value: str) -> Any:
        try:
            return cls._enum_value_map_[value]
        except (KeyError, TypeError):
            raise ValueError(f"{value!r} is not a valid {cls.__name__}")

    def __getitem__(cls, key: str) -> Any:
        return cls._enum_member_map_[key]

    def __setattr__(cls, name: str, value: Any) -> None:
        raise TypeError("Enums are immutable")

    def __delattr__(cls, attr: str) -> None:
        raise TypeError("Enums are immutable")

    def __instancecheck__(self, instance: Any) -> bool:
        # isinstance(x, Y)
        # -> __instancecheck__(Y, x)
        try:
            return instance._actual_enum_cls_ is self
        except AttributeError:
            return False


if TYPE_CHECKING:
    from enum import Enum
else:

    class Enum(metaclass=EnumMeta):
        @classmethod
        def try_value(cls, value):
            try:
                return cls._enum_value_map_[value]
            except (KeyError, TypeError):
                return value


class ChannelType(Enum):
    text = 0
    private = 1
    voice = 2
    group = 3
    category = 4
    news = 5
    store = 6
    news_thread = 10
    public_thread = 11
    private_thread = 12
    stage_voice = 13
    directory = 14
    forum = 15

    def __str__(self) -> str:
        return self.name

    def __int__(self):
        return self.value


class MessageType(Enum):
    default = 0
    recipient_add = 1
    recipient_remove = 2
    call = 3
    channel_name_change = 4
    channel_icon_change = 5
    channel_pinned_message = 6
    pins_add = 6
    member_join = 7
    user_join = 7
    new_member = 7
    channel_follow_add = 12
    guild_stream = 13
    guild_discovery_disqualified = 14
    guild_discovery_requalified = 15
    guild_discovery_grace_period_initial_warning = 16
    guild_discovery_grace_period_final_warning = 17
    thread_created = 18
    reply = 19
    chat_input_command = 20
    context_menu_command = 23
    stage_start = 27
    stage_end = 28
    stage_speaker = 29
    stage_raise_hand = 30
    stage_topic = 31


class Status(Enum):
    online = "online"
    offline = "offline"
    idle = "idle"
    dnd = "dnd"
    do_not_disturb = "dnd"
    invisible = "invisible"
    unknown = "unknown"

    def __str__(self) -> str:
        return self.value


class ActivityType(Enum):
    unknown = -1
    playing = 0
    streaming = 1
    listening = 2
    watching = 3
    custom = 4
    competing = 5

    def __int__(self) -> int:
        return self.value


class ExpireBehaviour(Enum):
    remove_role = 0
    kick = 1

    def __int__(self) -> int:
        return self.value


ExpireBehavior = ExpireBehaviour


class InteractionType(Enum):
    ping = 1
    application_command = 2
    component = 3
    autocomplete = 4
    modal_submit = 5

    def __int__(self) -> int:
        return self.value


class ComponentType(Enum):
    action_row = 1
    button = 2
    select = 3
    text_input = 4

    def __int__(self) -> int:
        return self.value


class ButtonStyle(Enum):
    primary = 1
    secondary = 2
    success = 3
    danger = 4
    link = 5

    # Aliases
    blurple = 1
    grey = 2
    gray = 2
    green = 3
    red = 4
    url = 5

    def __int__(self) -> int:
        return self.value


class TextStyle(Enum):
    short = 1
    paragraph = 2

    # Aliases
    long = 2

    def __int__(self) -> int:
        return self.value


T = TypeVar("T")
E = TypeVar("E", bound="Enum")


class EntityType(Enum):
    stage_instance = 1
    voice = 2
    external = 3


class ApplicationCommandOptionType(Enum):
    subcommand = 1
    sub_command = 1
    subcommand_group = 2
    sub_command_group = 2
    string = 3
    integer = 4
    boolean = 5
    user = 6
    channel = 7
    role = 8
    mentionable = 9
    number = 10
    attachment = 11


AppCommandOptionType = ApplicationCommandOptionType


class ApplicationCommandType(Enum):
    chat_input = 1
    user = 2
    message = 3

    def __int__(self) -> int:
        return self.value


AppCommandType = ApplicationCommandType


class ClientType(Enum):
    web = "web"
    mobile = "mobile"
    desktop = "desktop"
    unknown = "unknown"

    def __str__(self) -> str:
        return self.value


# There are tons of different operating system/client enums in the API,
# so we try to unify them here
# They're normalized as the numbered enum, and converted from the stringified enum(s)
class OperatingSystem(Enum):
    windows = 1
    macos = 2
    linux = 3

    android = -1
    ios = -2
    unknown = -3

    @classmethod
    def from_string(cls, value: str) -> Self:
        lookup = {
            "windows": cls.windows,
            "win32": cls.windows,
            "macos": cls.macos,
            "darwin": cls.macos,
            "linux": cls.linux,
            "android": cls.android,
            "ios": cls.ios,
            "unknown": cls.unknown,
        }
        return lookup.get(value, create_unknown_value(cls, value))

    def to_string(self):
        lookup = {
            OperatingSystem.windows: "win32",
            OperatingSystem.macos: "darwin",
            OperatingSystem.linux: "linux",
            OperatingSystem.android: "android",
            OperatingSystem.ios: "ios",
            OperatingSystem.unknown: "unknown",
        }
        return lookup[self]

    def __str__(self):
        return self.to_string()


class ReadStateType(Enum):
    channel = 0
    scheduled_events = 1
    notification_center = 2
    guild_home = 3
    onboarding = 4


def create_unknown_value(cls: Type[E], val: Any) -> E:
    value_cls = cls._enum_value_cls_  # type: ignore # This is narrowed below
    name = f"unknown_{val}"
    return value_cls(name=name, value=val)


def try_enum(cls: Type[E], val: Any) -> E:
    """A function that tries to turn the value into enum ``cls``.

    If it fails it returns a proxy invalid value instead.
    """

    try:
        return cls._enum_value_map_[val]  # type: ignore # All errors are caught below
    except (KeyError, TypeError, AttributeError):
        return create_unknown_value(cls, val)
