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

from typing import (
    TYPE_CHECKING,
)

from . import utils
from .mixins import Hashable

if TYPE_CHECKING:
    from .state import ConnectionState
    from .types.application import (
        BaseApplication as BaseApplicationPayload,
    )

__all__ = ("IntegrationApplication",)

MISSING = utils.MISSING


class IntegrationApplication(Hashable):
    """Represents a very partial application received in integration/interaction contexts.

    .. container:: operations

        .. describe:: x == y

            Checks if two applications are equal.

        .. describe:: x != y

            Checks if two applications are not equal.

        .. describe:: hash(x)

            Return the application's hash.

        .. describe:: str(x)

            Returns the application's name.

    .. versionadded:: 2.0

    Attributes
    -------------
    id: :class:`int`
        The application ID.
    name: :class:`str`
        The application name.
    """

    __slots__ = ("_state", "id", "name")

    def __init__(self, *, state: ConnectionState, data: BaseApplicationPayload):
        self._state: ConnectionState = state
        self._update(data)

    def __str__(self) -> str:
        return self.name

    def _update(self, data: BaseApplicationPayload) -> None:
        self.id: int = int(data["id"])

    def __repr__(self) -> str:
        return f"<IntegrationApplication id={self.id} name={self.name!r}>"
