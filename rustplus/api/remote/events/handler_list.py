from typing import Set, Dict
from .registered_listener import RegisteredListener


class HandlerList:
    def __init__(self) -> None:
        self._handlers: Set[RegisteredListener] = set()

    def unregister(self, listener: RegisteredListener) -> None:
        self._handlers.remove(listener)

    def register(self, listener: RegisteredListener) -> None:
        self._handlers.add(listener)

    def has(self, listener: RegisteredListener) -> bool:
        return listener in self._handlers

    def unregister_all(self) -> None:
        self._handlers.clear()

    def get_handlers(self):
        return self._handlers


class EntityHandlerList(HandlerList):
    def __init__(self) -> None:
        self._handlers: Dict[str, Set[RegisteredListener]] = {}

    def unregister(self, listener: RegisteredListener) -> None:
        self._handlers[listener.listener_id].remove(listener)

    def register(self, listener: RegisteredListener) -> None:
        if listener.listener_id not in self._handlers:
            self._handlers[listener.listener_id] = set()

        self._handlers[listener.listener_id].add(listener)

    def has(self, listener: RegisteredListener) -> bool:
        if listener.listener_id in self._handlers:
            return listener in self._handlers[listener.listener_id]

        return False

    def unregister_all(self) -> None:
        self._handlers.clear()
