import dataclasses
from collections import defaultdict
from typing import Dict, List

from .chat_command_data import ChatCommandData
from ..identification import ServerID


@dataclasses.dataclass
class ChatCommandTime:
    formatted_time: str
    raw_time: int


class ChatCommand:

    REGISTERED_COMMANDS: Dict[ServerID, Dict[str, ChatCommandData]] = defaultdict(dict)

    def __init__(
        self,
        sender_name: str,
        sender_steam_id: int,
        time: ChatCommandTime,
        command: str,
        args: List[str],
    ) -> None:
        self.sender_name = sender_name
        self.sender_steam_id = sender_steam_id
        self.time = time
        self.command = command
        self.args = args
