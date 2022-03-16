class RustChatMessage:
    def __init__(self, data):
        self._steam_id: int = data.steamId
        self._name: str = data.name
        self._message: str = data.message
        self._colour: str = data.color
        self._time: int = data.time

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
    def colour(self) -> str:
        return self._colour

    @property
    def time(self) -> int:
        return self._time

    def __repr__(self):
        return "RustChatMessage[steam_id={}, sender_name={}, message={}, colour={}, time={}]".format(
            self._steam_id, self._name, self._message, self._colour, self._time
        )
