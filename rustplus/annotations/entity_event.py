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

    if not isinstance(server_details, ServerDetails):
        if callable(server_details):
            message = ("EntityEvent decorator requires a ServerDetails object as an argument. You have probably "
                       "forgotten the brackets on the decorator to pass the server details object.")
        else:
            message = ("EntityEvent decorator requires a ServerDetails object as an argument. Please provide a valid "
                       "ServerDetails instance.")
        raise TypeError(message)

    return wrapper
