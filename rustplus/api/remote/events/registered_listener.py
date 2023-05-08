from typing import Union


class RegisteredListener:
    def __init__(self, listener_id: Union[str, int], data) -> None:
        self.listener_id = str(listener_id)
        self.data = data

    def get_coro(self):
        if isinstance(self.data, tuple):
            return self.data[0]
        return self.data

    def __eq__(self, other) -> bool:
        if isinstance(other, RegisteredListener):
            coro = self.data
            if isinstance(self.data, tuple):
                coro = self.data[0]

            return self.listener_id == other.listener_id and coro == coro
        return False

    def __hash__(self):
        coro = self.data
        if isinstance(self.data, tuple):
            coro = self.data[0]
        return hash((self.listener_id, coro))
