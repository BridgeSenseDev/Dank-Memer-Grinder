"""
Discord API Wrapper
~~~~~~~~~~~~~~~~~~~

A basic wrapper for the Discord user API.

:copyright: (c) 2015-present Rapptz and 2021-present Dolfies
:license: MIT, see LICENSE for more details.
"""

__title__ = "discord.py-self"
__author__ = "Dolfies"
__license__ = "MIT"
__copyright__ = "Copyright 2015-present Rapptz and 2021-present Dolfies"
__version__ = "2.1.0a"

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

import logging
from typing import Literal, NamedTuple

from . import abc as abc, utils as utils
from .application import *
from .asset import *
from .channel import *
from .client import *
from .colour import *
from .commands import *
from .components import *
from .embeds import *
from .emoji import *
from .enums import *
from .errors import *
from .file import *
from .flags import *
from .guild import *
from .interactions import *
from .message import *
from .metadata import *
from .modal import *
from .object import *
from .oauth2 import *
from .partial_emoji import *
from .raw_models import *
from .read_state import *
from .user import *


class _VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: Literal["alpha", "beta", "candidate", "final"]
    serial: int


version_info: _VersionInfo = _VersionInfo(
    major=2, minor=1, micro=0, releaselevel="alpha", serial=0
)

logging.getLogger(__name__).addHandler(logging.NullHandler())


del logging, NamedTuple, Literal, _VersionInfo
