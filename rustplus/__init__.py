r"""
RustPlus, An API wrapper for interfacing with the Rust+ App API
"""

from .api import RustSocket
from .api.remote.events import (
    EntityEvent,
    TeamEvent,
    ChatEvent,
    MarkerEvent,
    ProtobufEvent,
    RegisteredListener,
)
from .api.structures import RustMarker, Vector
from .api.remote.fcm_listener import FCMListener
from .api.remote.ratelimiter import RateLimiter
from .api.remote.camera import CameraManager, MovementControls, CameraMovementOptions
from .commands import CommandOptions, Command
from .exceptions import *
from .conversation import ConversationFactory, Conversation, ConversationPrompt
from .utils import *

__name__ = "rustplus"
__author__ = "olijeffers0n"
__version__ = "5.6.9"
__support__ = "Discord: https://discord.gg/nQqJe8qvP8"
