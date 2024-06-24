from ..remote.handler_list import HandlerList
from ..structs import RustChatMessage


class ChatEventPayload:
    HANDLER_LIST = HandlerList()

    def __init__(self, message: RustChatMessage) -> None:
        self._message = message

    @property
    def message(self) -> RustChatMessage:
        return self._message
