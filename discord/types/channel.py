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

from typing import List, Literal, Optional, TypedDict, Union
from typing_extensions import NotRequired

from .user import PartialUser
from .snowflake import Snowflake

OverwriteType = Literal[0, 1]


class PermissionOverwrite(TypedDict):
    id: Snowflake
    type: OverwriteType
    allow: str
    deny: str


ChannelTypeWithoutThread = Literal[0, 1, 2, 3, 4, 5, 6, 13, 14, 15]
ChannelType = Union[ChannelTypeWithoutThread]


class _BaseChannel(TypedDict):
    id: Snowflake


class _BaseGuildChannel(_BaseChannel):
    guild_id: Snowflake
    position: int
    permission_overwrites: List[PermissionOverwrite]
    parent_id: Optional[Snowflake]
    name: str
    flags: int


class PartialRecipient(TypedDict):
    username: str


class PartialChannel(_BaseChannel):
    name: Optional[str]
    type: ChannelType
    icon: NotRequired[Optional[str]]
    recipients: NotRequired[List[PartialRecipient]]


class _BaseTextChannel(_BaseGuildChannel, total=False):
    topic: str
    last_message_id: Optional[Snowflake]
    rate_limit_per_user: int


class TextChannel(_BaseTextChannel):
    type: Literal[0]


class CategoryChannel(_BaseGuildChannel):
    type: Literal[4]


GuildChannel = Union[TextChannel, CategoryChannel]


class DMChannel(_BaseChannel):
    type: Literal[1]
    last_message_id: Optional[Snowflake]
    recipients: List[PartialUser]
    is_message_request: NotRequired[bool]
    is_message_request_timestamp: NotRequired[str]
    is_spam: NotRequired[bool]


Channel = Union[GuildChannel, DMChannel]
