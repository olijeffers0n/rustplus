import asyncio
from asyncio.futures import Future
from typing import Set

from .events import EntityEvent, TeamEvent, ChatEvent, ProtobufEvent
from .registered_listener import RegisteredListener
from .event_loop_manager import EventLoopManager


class EventHandler:
    @staticmethod
    def _schedule_event(loop, coro, arg) -> None:
        def callback(inner_future: Future):
            inner_future.result()

        future: Future = asyncio.run_coroutine_threadsafe(coro(arg), loop)
        future.add_done_callback(callback)

    def run_entity_event(self, name, app_message, server_id) -> None:

        handlers: Set[RegisteredListener] = EntityEvent.handlers.get_handlers(
            server_id
        ).get(str(name))

        if handlers is None:
            return

        for handler in handlers.copy():
            coro, event_type = handler.data

            self._schedule_event(
                EventLoopManager.get_loop(server_id),
                coro,
                EntityEvent(app_message, event_type),
            )

    def run_team_event(self, app_message, server_id) -> None:

        handlers: Set[RegisteredListener] = TeamEvent.handlers.get_handlers(server_id)
        for handler in handlers.copy():
            coro = handler.data

            self._schedule_event(
                EventLoopManager.get_loop(server_id), coro, TeamEvent(app_message)
            )

    def run_chat_event(self, app_message, server_id) -> None:

        handlers: Set[RegisteredListener] = ChatEvent.handlers.get_handlers(server_id)
        for handler in handlers.copy():
            coro = handler.data

            self._schedule_event(
                EventLoopManager.get_loop(server_id), coro, ChatEvent(app_message)
            )

    def run_proto_event(self, byte_data: bytes, server_id) -> None:

        handlers: Set[RegisteredListener] = ProtobufEvent.handlers.get_handlers(
            server_id
        )
        for handler in handlers.copy():
            coro = handler.data

            self._schedule_event(
                EventLoopManager.get_loop(server_id), coro, ProtobufEvent(byte_data)
            )
