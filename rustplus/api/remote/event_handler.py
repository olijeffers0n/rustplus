import asyncio
from asyncio.futures import Future
from typing import List

from ..structures import EntityEvent, TeamEvent, ChatEvent

class EventHandler:

    def __init__(self) -> None:
        pass

    def register_event(self, name, data : tuple) -> None:

        if not asyncio.iscoroutinefunction(data[0]):
            raise TypeError("The event registered must be a coroutine")

        if hasattr(self, str(name)):
            events : List[tuple] = getattr(self, str(name))
            events.append(data)
            setattr(self, str(name), events)
        else:
            setattr(self, str(name), [data])

    def _schedule_event(self, loop, coro, arg) -> None:

        def callback(future : Future):
            future.result()

        future : Future = asyncio.run_coroutine_threadsafe(coro(arg), loop)
        future.add_done_callback(callback)

    def run_entity_event(self, name, app_message) -> None:

        if hasattr(self, str(name)):
            for event in getattr(self, str(name)):
                coro, loop, type = event

                self._schedule_event(loop, coro, EntityEvent(app_message, type)) # I reconstruct the Event Object for each of these each time as i dont want the object to be mitakenly changed by one event, messing up subsequent events

    def run_team_event(self, app_message) -> None:

        if hasattr(self, "team_changed"):
            for event in getattr(self, "team_changed"):
                coro, loop = event

                self._schedule_event(loop, coro, TeamEvent(app_message))

    def run_chat_event(self, app_message) -> None:

        if hasattr(self, "chat_message"):
            for event in getattr(self, "chat_message"):
                coro, loop = event

                self._schedule_event(loop, coro, ChatEvent(app_message))
