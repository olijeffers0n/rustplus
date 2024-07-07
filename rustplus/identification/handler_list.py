from collections import defaultdict
from typing import Set, Dict
from rustplus.identification import (
    RegisteredListener,
    RegisteredEntityListener,
    ServerDetails,
)


class HandlerList:
    def __init__(self) -> None:
        self._handlers: Dict[ServerDetails, Set[RegisteredListener]] = defaultdict(set)

    def unregister(
        self, listener: RegisteredListener, server_details: ServerDetails
    ) -> None:
        self._handlers[server_details].remove(listener)

    def register(
        self, listener: RegisteredListener, server_details: ServerDetails
    ) -> None:
        self._handlers[server_details].add(listener)

    def has(self, listener: RegisteredListener, server_details: ServerDetails) -> bool:
        return listener in self._handlers[server_details]

    def unregister_all(self) -> None:
        self._handlers.clear()

    def get_handlers(self, server_details: ServerDetails) -> Set[RegisteredListener]:
        return self._handlers.get(server_details, set())


class EntityHandlerList(HandlerList):
    def __init__(self) -> None:
        super().__init__()
        self._handlers: Dict[
            ServerDetails, Dict[str, Set[RegisteredEntityListener]]
        ] = defaultdict(dict)

    def unregister(
        self, listener: RegisteredEntityListener, server_details: ServerDetails
    ) -> None:
        if listener.listener_id in self._handlers.get(server_details):
            self._handlers.get(server_details).get(listener.listener_id).remove(
                listener
            )

    def register(
        self, listener: RegisteredEntityListener, server_details: ServerDetails
    ) -> None:
        if server_details not in self._handlers:
            self._handlers[server_details] = defaultdict(set)

        if listener.listener_id not in self._handlers.get(server_details):
            self._handlers.get(server_details)[listener.listener_id] = set()

        self._handlers.get(server_details).get(listener.listener_id).add(listener)

    def has(
        self, listener: RegisteredEntityListener, server_details: ServerDetails
    ) -> bool:
        if (
            server_details in self._handlers
            and listener.listener_id in self._handlers.get(server_details)
        ):
            return listener in self._handlers.get(server_details).get(
                listener.listener_id
            )

        return False

    def unregister_all(self) -> None:
        self._handlers.clear()

    def get_handlers(
        self, server_details: ServerDetails
    ) -> Dict[str, Set[RegisteredEntityListener]]:
        return self._handlers.get(server_details, dict())
