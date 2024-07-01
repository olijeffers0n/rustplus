from typing import Callable

from .. import ServerDetails
from ..identification import RegisteredListener
from ..events import ProtobufEventPayload as ProtobufEventManager


def ProtobufEvent(server_details: ServerDetails) -> Callable:
    def wrapper(func) -> RegisteredListener:
        if isinstance(func, RegisteredListener):
            func = func.get_coro()

        listener = RegisteredListener(func.__name__, func)

        ProtobufEventManager.HANDLER_LIST.register(listener, server_details)

        return listener

    return wrapper
