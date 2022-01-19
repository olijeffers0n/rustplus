r"""
RustPlus, An API wrapper for interfacing with the Rust+ App API
"""

from .api import RustSocket
from .commands import CommandOptions, Command
from .exceptions import *
from .api.structures import EntityEvent, TeamEvent, ChatEvent
from .utils import entity_type_to_string, convert_xy_to_grid

__name__ = "rustplus"
__author__ = "olijefferson"
__version__ = "5.2.1"
__support__ = "Discord: https://discord.gg/nQqJe8qvP8"
