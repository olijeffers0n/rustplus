from typing import Callable

from .. import ServerDetails
from ..identification import RegisteredListener
from ..events import TeamEventPayload as TeamEventManager


def TeamEvent(server_details: ServerDetails) -> Callable:
    def wrapper(func) -> RegisteredListener:
        if isinstance(func, RegisteredListener):
            func = func.get_coro()

        listener = RegisteredListener(func.__name__, func)

        TeamEventManager.HANDLER_LIST.register(listener, server_details)

        return listener

    return wrapper
