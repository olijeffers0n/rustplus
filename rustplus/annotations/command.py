from typing import Callable

from ..identification import RegisteredListener, ServerDetails
from ..commands import ChatCommand, ChatCommandData


def Command(
    server_details: ServerDetails, aliases: list = None, alias_func: Callable = None
) -> Callable:

    def wrapper(func):

        if isinstance(func, RegisteredListener):
            func = func.get_coro()

        command_data = ChatCommandData(
            coroutine=func, aliases=aliases, callable_func=alias_func
        )
        ChatCommand.REGISTERED_COMMANDS[server_details][func.__name__] = command_data

        return RegisteredListener(func.__name__, func)

    if not isinstance(server_details, ServerDetails):
        if callable(server_details):
            message = ("Command decorator requires a ServerDetails object as an argument. You have probably "
                       "forgotten the brackets on the decorator to pass the server details object.")
        else:
            message = ("Command decorator requires a ServerDetails object as an argument. Please provide a valid "
                       "ServerDetails instance.")
        raise TypeError(message)

    return wrapper
