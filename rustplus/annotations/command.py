from typing import Callable

from ..identification import RegisteredListener, ServerID
from ..commands import ChatCommand, ChatCommandData


def Command(server_id: ServerID, aliases: list = None, alias_func: Callable = None):

    def wrapper(func):

        if isinstance(func, RegisteredListener):
            func = func.get_coro()

        command_data = ChatCommandData(coroutine=func, aliases=aliases, callable_func=alias_func)
        ChatCommand.REGISTERED_COMMANDS[server_id][func.__name__] = command_data

        return RegisteredListener(func.__name__, func)

    return wrapper
