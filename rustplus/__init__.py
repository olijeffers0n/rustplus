r"""
RustPlus, An API wrapper for interfacing with the Rust+ App API
"""

from .rust_api import RustSocket
from .identification import ServerID
from .annotations import Command, ChatEvent, ProtobufEvent, TeamEvent, EntityEvent
from .commands import CommandOptions
from .events import ChatEventPayload, TeamEventPayload, EntityEventPayload

__name__ = "rustplus"
__author__ = "olijeffers0n"
__version__ = "6.0.0"
__support__ = "Discord: https://discord.gg/nQqJe8qvP8"
