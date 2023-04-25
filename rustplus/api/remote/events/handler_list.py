from collections import defaultdict
from typing import Set, Dict
from .registered_listener import RegisteredListener
from ....utils import ServerID


class HandlerList:
    def __init__(self) -> None:
        self._handlers: Dict[ServerID, Set[RegisteredListener]] = defaultdict(set)

    def unregister(self, listener: RegisteredListener, server_id: ServerID) -> None:
        self._handlers[server_id].remove(listener)

    def register(self, listener: RegisteredListener, server_id: ServerID) -> None:
        self._handlers[server_id].add(listener)

    def has(self, listener: RegisteredListener, server_id: ServerID) -> bool:
        return listener in self._handlers[server_id]

    def unregister_all(self) -> None:
        self._handlers.clear()

    def get_handlers(
        self, server_id: ServerID
    ) -> Dict[ServerID, Set[RegisteredListener]]:
        return self._handlers.get(server_id, set())


class EntityHandlerList(HandlerList):
    def __init__(self) -> None:
        self._handlers: Dict[
            ServerID, Dict[str, Set[RegisteredListener]]
        ] = defaultdict(dict)

    def unregister(self, listener: RegisteredListener, server_id: ServerID) -> None:
        if listener.listener_id in self._handlers.get(server_id):
            self._handlers.get(server_id).get(listener.listener_id).remove(listener)

    def register(self, listener: RegisteredListener, server_id: ServerID) -> None:

        if server_id not in self._handlers:
            self._handlers[server_id] = defaultdict(set)

        if listener.listener_id not in self._handlers.get(server_id):
            self._handlers.get(server_id)[listener.listener_id] = set()

        self._handlers.get(server_id).get(listener.listener_id).add(listener)

    def has(self, listener: RegisteredListener, server_id: ServerID) -> bool:
        if server_id in self._handlers and listener.listener_id in self._handlers.get(
            server_id
        ):
            return listener in self._handlers.get(server_id).get(listener.listener_id)

        return False

    def unregister_all(self) -> None:
        self._handlers.clear()

    def get_handlers(
        self, server_id: ServerID
    ) -> Dict[ServerID, Set[RegisteredListener]]:
        return self._handlers.get(server_id, dict())
