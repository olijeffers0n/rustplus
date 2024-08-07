from typing import Callable


class ChatCommandData:

    def __init__(self, coroutine: Callable, aliases=None, callable_func=None) -> None:
        self.coroutine = coroutine
        self._aliases = aliases
        self._callable_func = callable_func

    @property
    def aliases(self):
        if self._aliases is None:
            return []

        return self._aliases

    @property
    def callable_func(self):
        if self._callable_func is None:
            return lambda x: False

        return self._callable_func
