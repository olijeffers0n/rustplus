from typing import Union, Coroutine


class RegisteredListener:
    def __init__(
        self,
        listener_id: Union[str, int],
        coroutine: Coroutine,
        entity_type: int = None,
    ) -> None:
        self.listener_id = str(listener_id)
        self._coroutine = coroutine
        self._entity_type = entity_type

    def get_coro(self):
        return self._coroutine

    def get_entity_type(self):
        return self._entity_type

    def __eq__(self, other) -> bool:
        if not isinstance(other, RegisteredListener):
            return False

        return (
            self.listener_id == other.listener_id
            and self._coroutine == other.get_coro()
            and self._entity_type == other.get_entity_type()
        )

    def __hash__(self):
        return hash((self.listener_id, self._coroutine, self._entity_type))
