from typing import Callable

from .. import ServerDetails
from ..identification import RegisteredEntityListener, RegisteredListener
from ..events import EntityEventPayload as EntityEventManager


def EntityEvent(server_details: ServerDetails, eid: int) -> Callable:
    def wrapper(func) -> RegisteredListener:
        if isinstance(func, RegisteredListener):
            func = func.get_coro()

        listener = RegisteredEntityListener(
            str(eid), func, 1
        )  # TODO, how are we going to handle the entity type?

        EntityEventManager.HANDLER_LIST.register(listener, server_details)

        return listener

    return wrapper
