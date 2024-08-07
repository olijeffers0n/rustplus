from rustplus.identification.handler_list import HandlerList


class ProtobufEventPayload:
    HANDLER_LIST = HandlerList()

    def __init__(self, message: bytes) -> None:
        self._message = message

    @property
    def message(self) -> bytes:
        return self._message
