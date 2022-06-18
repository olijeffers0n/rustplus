import asyncio
from asyncio.futures import Future
from typing import List

from ..structures import EntityEvent, TeamEvent, ChatEvent
from ...utils import RegisteredListener


class EventHandler:
    def __init__(self) -> None:
        pass

    def register_event(self, listener: RegisteredListener) -> None:

        if not asyncio.iscoroutinefunction(listener.data[0]):
            raise TypeError("The event registered must be a coroutine")

        if hasattr(self, str(listener.listener_id)):
            events: List[RegisteredListener] = getattr(self, str(listener.listener_id))
            events.append(listener)
            setattr(self, str(listener.listener_id), events)
        else:
            setattr(self, str(listener.listener_id), [listener])

    @staticmethod
    def _schedule_event(loop, coro, arg) -> None:
        def callback(inner_future: Future):
            inner_future.result()

        future: Future = asyncio.run_coroutine_threadsafe(coro(arg), loop)
        future.add_done_callback(callback)

    def run_entity_event(self, name, app_message) -> None:

        if hasattr(self, str(name)):
            for event in getattr(self, str(name)):
                coro, loop, event_type = event.data

                self._schedule_event(loop, coro, EntityEvent(app_message, event_type))

    def run_team_event(self, app_message) -> None:

        if hasattr(self, "team_changed"):
            for event in getattr(self, "team_changed"):
                coro, loop = event.data

                self._schedule_event(loop, coro, TeamEvent(app_message))

    def run_chat_event(self, app_message) -> None:

        if hasattr(self, "chat_message"):
            for event in getattr(self, "chat_message"):
                coro, loop = event.data

                self._schedule_event(loop, coro, ChatEvent(app_message))

    def run_proto_event(self, byte_data: bytes) -> None:

        if hasattr(self, "protobuf_received"):
            for event in getattr(self, "protobuf_received"):
                coro, loop = event.data

                self._schedule_event(loop, coro, byte_data)

    def has_event(self, listener: RegisteredListener) -> bool:
        if hasattr(self, listener.listener_id):
            return listener in list(getattr(self, listener.listener_id))
        return False

    def remove_event(self, listener: RegisteredListener) -> None:
        if hasattr(self, listener.listener_id):
            events = list(getattr(self, listener.listener_id))
            try:
                while True:
                    events.remove(listener)
            except ValueError:
                pass
            setattr(self, listener.listener_id, events)

    def clear_entity_events(self) -> None:

        to_remove = []
        for name in vars(self).keys():
            # only remove entity events
            if name not in ["team_changed", "chat_message", "protobuf_received"]:
                to_remove.append(name)

        for name in to_remove:
            delattr(self, name)
