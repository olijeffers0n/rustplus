from typing import Callable

from .. import ServerID
from ..identification import RegisteredListener
from ..events import TeamEvent as TeamEventManager


def TeamEvent(server_id: ServerID) -> Callable:
    def wrapper(func) -> RegisteredListener:
        if isinstance(func, RegisteredListener):
            func = func.get_coro()

        listener = RegisteredListener(func.__name__, func)

        TeamEventManager.HANDLER_LIST.register(listener, server_id)

        return listener

    return wrapper
