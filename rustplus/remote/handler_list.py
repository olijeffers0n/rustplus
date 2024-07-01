from collections import defaultdict
from typing import Set, Dict
from ..identification import RegisteredListener, RegisteredEntityListener, ServerDetails


class HandlerList:
    def __init__(self) -> None:
        self._handlers: Dict[ServerDetails, Set[RegisteredListener]] = defaultdict(set)

    def unregister(self, listener: RegisteredListener, server_id: ServerDetails) -> None:
        self._handlers[server_id].remove(listener)

    def register(self, listener: RegisteredListener, server_id: ServerDetails) -> None:
        self._handlers[server_id].add(listener)

    def has(self, listener: RegisteredListener, server_id: ServerDetails) -> bool:
        return listener in self._handlers[server_id]

    def unregister_all(self) -> None:
        self._handlers.clear()

    def get_handlers(self, server_id: ServerDetails) -> Set[RegisteredListener]:
        return self._handlers.get(server_id, set())


class EntityHandlerList(HandlerList):
    def __init__(self) -> None:
        super().__init__()
        self._handlers: Dict[ServerDetails, Dict[str, Set[RegisteredEntityListener]]] = (
            defaultdict(dict)
        )

    def unregister(
        self, listener: RegisteredEntityListener, server_id: ServerDetails
    ) -> None:
        if listener.listener_id in self._handlers.get(server_id):
            self._handlers.get(server_id).get(listener.listener_id).remove(listener)

    def register(self, listener: RegisteredEntityListener, server_id: ServerDetails) -> None:
        if server_id not in self._handlers:
            self._handlers[server_id] = defaultdict(set)

        if listener.listener_id not in self._handlers.get(server_id):
            self._handlers.get(server_id)[listener.listener_id] = set()

        self._handlers.get(server_id).get(listener.listener_id).add(listener)

    def has(self, listener: RegisteredEntityListener, server_id: ServerDetails) -> bool:
        if server_id in self._handlers and listener.listener_id in self._handlers.get(
            server_id
        ):
            return listener in self._handlers.get(server_id).get(listener.listener_id)

        return False

    def unregister_all(self) -> None:
        self._handlers.clear()

    def get_handlers(
        self, server_id: ServerDetails
    ) -> Dict[str, Set[RegisteredEntityListener]]:
        return self._handlers.get(server_id, dict())
