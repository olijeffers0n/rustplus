r"""
RustPlus, An API wrapper for interfacing with the Rust+ App API
"""

from .api import RustSocket
from .api.remote.camera import (CameraManager, CameraMovementOptions,
                                MovementControls)
from .api.remote.events import (ChatEvent, EntityEvent, MarkerEvent,
                                ProtobufEvent, RegisteredListener, TeamEvent)
from .api.remote.fcm_listener import FCMListener
from .api.remote.ratelimiter import RateLimiter
from .api.structures import RustMarker, Vector
from .commands import Command, CommandOptions
from .conversation import Conversation, ConversationFactory, ConversationPrompt
from .exceptions import *
from .utils import *

__name__ = "rustplus"
__author__ = "olijeffers0n"
__version__ = "5.5.13"
__support__ = "Discord: https://discord.gg/nQqJe8qvP8"
