import asyncio
from asyncio.futures import Future
from typing import Set

from .events import EntityEvent, TeamEvent, ChatEvent, ProtobufEvent
from .registered_listener import RegisteredListener


class EventHandler:
    @staticmethod
    def _schedule_event(loop, coro, arg) -> None:
        def callback(inner_future: Future):
            inner_future.result()

        future: Future = asyncio.run_coroutine_threadsafe(coro(arg), loop)
        future.add_done_callback(callback)

    def run_entity_event(self, name, app_message) -> None:

        handlers: Set[RegisteredListener] = EntityEvent.handlers.get_handlers().get(
            str(name)
        )

        if handlers is None:
            return

        for handler in handlers.copy():
            coro, loop, event_type = handler.data

            self._schedule_event(loop, coro, EntityEvent(app_message, event_type))

    def run_team_event(self, app_message) -> None:

        handlers: Set[RegisteredListener] = TeamEvent.handlers.get_handlers()
        for handler in handlers.copy():
            coro, loop = handler.data

            self._schedule_event(loop, coro, TeamEvent(app_message))

    def run_chat_event(self, app_message) -> None:

        handlers: Set[RegisteredListener] = ChatEvent.handlers.get_handlers()
        for handler in handlers.copy():
            coro, loop = handler.data

            self._schedule_event(loop, coro, ChatEvent(app_message))

    def run_proto_event(self, byte_data: bytes) -> None:

        handlers: Set[RegisteredListener] = ProtobufEvent.handlers.get_handlers()
        for handler in handlers.copy():
            coro, loop = handler.data

            self._schedule_event(loop, coro, ProtobufEvent(byte_data))
