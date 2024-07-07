r"""
RustPlus, An API wrapper for interfacing with the Rust+ App API
"""

from .rust_api import RustSocket
from .identification import ServerDetails
from .annotations import Command, ChatEvent, ProtobufEvent, TeamEvent, EntityEvent
from .remote.fcm import FCMListener
from .commands import CommandOptions
from .events import ChatEventPayload, TeamEventPayload, EntityEventPayload
from .utils import convert_event_type_to_name

__name__ = "rustplus"
__author__ = "olijeffers0n"
__version__ = "6.0.0"
__support__ = "Discord: https://discord.gg/nQqJe8qvP8"
