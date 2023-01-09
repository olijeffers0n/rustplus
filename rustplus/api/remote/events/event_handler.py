import asyncio
from asyncio.futures import Future

from .events import EntityEvent, TeamEvent, ChatEvent


class EventHandler:

    @staticmethod
    def _schedule_event(loop, coro, arg) -> None:
        def callback(inner_future: Future):
            inner_future.result()

        future: Future = asyncio.run_coroutine_threadsafe(coro(arg), loop)
        future.add_done_callback(callback)

    def run_entity_event(self, name, app_message) -> None:

        raise NotImplementedError("Not Implemented")
        if hasattr(self, str(name)):
            for event in getattr(self, str(name)):
                coro, loop, event_type = event.data

                self._schedule_event(loop, coro, EntityEvent(app_message, event_type))

    def run_team_event(self, app_message) -> None:

        raise NotImplementedError("Not Implemented")
        if hasattr(self, "team_changed"):
            for event in getattr(self, "team_changed"):
                coro, loop = event.data

                self._schedule_event(loop, coro, TeamEvent(app_message))

    def run_chat_event(self, app_message) -> None:

        raise NotImplementedError("Not Implemented")
        if hasattr(self, "chat_message"):
            for event in getattr(self, "chat_message"):
                coro, loop = event.data

                self._schedule_event(loop, coro, ChatEvent(app_message))

    def run_proto_event(self, byte_data: bytes) -> None:

        raise NotImplementedError("Not Implemented")
        if hasattr(self, "protobuf_received"):
            for event in getattr(self, "protobuf_received"):
                coro, loop = event.data

                self._schedule_event(loop, coro, byte_data)
