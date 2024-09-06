from typing import Coroutine


class RegisteredListener:
    def __init__(
        self,
        listener_id: str,
        coroutine: Coroutine,
    ) -> None:
        self.listener_id = listener_id
        self._coroutine = coroutine

    def get_coro(self):
        return self._coroutine

    def __eq__(self, other) -> bool:
        if not isinstance(other, RegisteredListener):
            return False

        return (
            self.listener_id == other.listener_id
            and self._coroutine == other.get_coro()
        )

    def __hash__(self):
        return hash((self.listener_id, self._coroutine))
