from ..remote.rustplus_proto import AppClanMessage


class RustClanMessage:
    def __init__(self, message: AppClanMessage) -> None:
        self._steam_id: int = message.steam_id
        self._name: str = message.name
        self._message: str = message.message
        self._timestamp: int = message.time

    @property
    def steam_id(self) -> int:
        return self._steam_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def message(self) -> str:
        return self._message

    @property
    def timestamp(self) -> int:
        return self._timestamp
