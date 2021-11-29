r"""
RustPlus, An API wrapper for interfacing with the Rust+ App API
"""

from .api import RustSocket
from .exceptions import ClientError, ImageError, ServerNotResponsiveError, ClientNotConnectedError, PrefixNotDefinedError, CommandsNotEnabledError
from .commands import CommandOptions, Command

__name__ = "rustplus"
__author__ = "olijefferson"
__version__ = "4.1.0"
__support__ = "Discord: https://discord.gg/nQqJe8qvP8"
