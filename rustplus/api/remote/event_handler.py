import asyncio

from ..structures import EntityEvent

class EventHandler:

    def __init__(self) -> None:
        pass

    def register_event(self, name, data : tuple) -> None:

        if not asyncio.iscoroutinefunction(data[0]):
            raise TypeError("The event registered must be a coroutine")

        setattr(self, str(name), data)

    def _schedule_event(self, loop, coro, arg) -> None:
        asyncio.run_coroutine_threadsafe(coro(arg), loop)

    def run_event(self, name, app_message) -> None:

        if hasattr(self, str(name)):
            coro, loop, type = getattr(self, str(name))

            self._schedule_event(loop, coro, EntityEvent(app_message, type))
