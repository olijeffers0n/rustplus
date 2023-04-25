import asyncio
import logging
from asyncio.futures import Future
from typing import Any, Coroutine, Set

from ....utils import ServerID
from ..rustplus_proto import AppMessage
from .event_loop_manager import EventLoopManager
from .events import ChatEvent, EntityEvent, ProtobufEvent, TeamEvent
from .registered_listener import RegisteredListener


class EventHandler:
    @staticmethod
    def schedule_event(
        loop: asyncio.AbstractEventLoop, coro: Coroutine, arg: Any
    ) -> None:
        def callback(inner_future: Future):
            if inner_future.exception() is not None:
                logging.getLogger("rustplus.py").exception(inner_future.exception())

        future: Future = asyncio.run_coroutine_threadsafe(coro(arg), loop)
        future.add_done_callback(callback)

    def run_entity_event(
        self, name: str, app_message: AppMessage, server_id: ServerID
    ) -> None:
        handlers: Set[RegisteredListener] = EntityEvent.handlers.get_handlers(
            server_id
        ).get(str(name))

        if handlers is None:
            return

        for handler in handlers.copy():
            coro, event_type = handler.data

            self.schedule_event(
                EventLoopManager.get_loop(server_id),
                coro,
                EntityEvent(app_message, event_type),
            )

    def run_team_event(self, app_message: AppMessage, server_id: ServerID) -> None:
        handlers: Set[RegisteredListener] = TeamEvent.handlers.get_handlers(server_id)
        for handler in handlers.copy():
            coro = handler.data

            self.schedule_event(
                EventLoopManager.get_loop(server_id), coro, TeamEvent(app_message)
            )

    def run_chat_event(self, app_message: AppMessage, server_id: ServerID) -> None:
        handlers: Set[RegisteredListener] = ChatEvent.handlers.get_handlers(server_id)
        for handler in handlers.copy():
            coro = handler.data

            self.schedule_event(
                EventLoopManager.get_loop(server_id), coro, ChatEvent(app_message)
            )

    def run_proto_event(self, byte_data: bytes, server_id: ServerID) -> None:
        handlers: Set[RegisteredListener] = ProtobufEvent.handlers.get_handlers(
            server_id
        )
        for handler in handlers.copy():
            coro = handler.data

            self.schedule_event(
                EventLoopManager.get_loop(server_id), coro, ProtobufEvent(byte_data)
            )
