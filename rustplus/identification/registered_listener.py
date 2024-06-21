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


class RegisteredEntityListener(RegisteredListener):
    def __init__(
        self,
        listener_id: str,
        coroutine: Coroutine,
        entity_type: int,
    ) -> None:
        super().__init__(listener_id, coroutine)
        self.entity_type = entity_type

    def get_entity_type(self):
        return self.entity_type

    def __eq__(self, other) -> bool:
        if not isinstance(other, RegisteredEntityListener):
            return False

        return super().__eq__(other) and self.listener_id == other.listener_id

    def __hash__(self):
        return hash((self.listener_id, self._coroutine, self.entity_type))
