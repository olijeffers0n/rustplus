r"""
RustPlus, An API wrapper for interfacing with the Rust+ App API
"""

from .api import RustSocket
from .api.structures import EntityEvent, TeamEvent, ChatEvent
from .api.remote.fcm_listener import FCMListener
from .commands import CommandOptions, Command
from .exceptions import *
from .conversation import ConversationFactory, Conversation, ConversationPrompt
from .utils import *
from .module_info import ModuleInfo

__name__ = ModuleInfo.__module_name__
__author__ = ModuleInfo.__author__
__version__ = ModuleInfo.__version__
__support__ = ModuleInfo.__support__
