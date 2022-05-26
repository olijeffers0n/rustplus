from typing import Callable, List


class CommandData:
    def __init__(self, coro, loop, aliases, callable_func) -> None:
        self.coro = coro
        self.loop = loop
        self._aliases = aliases
        self._callable_func = callable_func

    @property
    def aliases(self) -> List[str]:
        if self._aliases is None:
            return []

        return self._aliases

    @property
    def callable_func(self) -> Callable:
        if self._callable_func is None:
            return lambda x: False

        return self._callable_func
