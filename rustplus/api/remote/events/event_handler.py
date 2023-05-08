from typing import Set, Union

from ....utils import ServerID
from .events import EntityEvent, TeamEvent, ChatEvent, ProtobufEvent
from .registered_listener import RegisteredListener
from ..rustplus_proto import AppMessage


class EventHandler:
    @staticmethod
    async def run_entity_event(
        name: Union[str, int], app_message: AppMessage, server_id: ServerID
    ) -> None:
        handlers: Set[RegisteredListener] = EntityEvent.handlers.get_handlers(
            server_id
        ).get(str(name))

        if handlers is None:
            return

        for handler in handlers.copy():
            coro, event_type = handler.data

            await coro(EntityEvent(app_message, event_type))

    @staticmethod
    async def run_team_event(app_message: AppMessage, server_id: ServerID) -> None:
        handlers: Set[RegisteredListener] = TeamEvent.handlers.get_handlers(server_id)
        for handler in handlers.copy():
            coro = handler.data

            await coro(TeamEvent(app_message))

    @staticmethod
    async def run_chat_event(app_message: AppMessage, server_id: ServerID) -> None:
        handlers: Set[RegisteredListener] = ChatEvent.handlers.get_handlers(server_id)
        for handler in handlers.copy():
            coro = handler.data

            await coro(ChatEvent(app_message))

    @staticmethod
    async def run_proto_event(byte_data: bytes, server_id: ServerID) -> None:
        handlers: Set[RegisteredListener] = ProtobufEvent.handlers.get_handlers(
            server_id
        )
        for handler in handlers.copy():
            coro = handler.data

            await coro(ProtobufEvent(byte_data))
