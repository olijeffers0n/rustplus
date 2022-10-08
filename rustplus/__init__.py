r"""
RustPlus, An API wrapper for interfacing with the Rust+ App API
"""

from .api import RustSocket
from .api.structures import EntityEvent, TeamEvent, ChatEvent, MarkerEvent, RustMarker
from .api.remote.fcm_listener import FCMListener
from .commands import CommandOptions, Command
from .exceptions import *
from .conversation import ConversationFactory, Conversation, ConversationPrompt
from .utils import *

__name__ = "rustplus"
__author__ = "olijeffers0n"
__version__ = "5.4.8"
__support__ = "Discord: https://discord.gg/nQqJe8qvP8"
