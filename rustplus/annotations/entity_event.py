from typing import Callable

from .. import ServerDetails
from ..identification import RegisteredListener
from ..events import EntityEventPayload as EntityEventManager


def EntityEvent(server_details: ServerDetails, eid: int) -> Callable:
    def wrapper(func) -> RegisteredListener:
        if isinstance(func, RegisteredListener):
            func = func.get_coro()

        listener = RegisteredListener(str(eid), func)

        EntityEventManager.HANDLER_LIST.register(listener, server_details)

        return listener

    return wrapper
