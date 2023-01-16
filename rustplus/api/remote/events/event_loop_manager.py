import asyncio
from ....utils import ServerID


class EventLoopManager:

    _loop = {}

    @staticmethod
    def get_loop(server_id: ServerID) -> asyncio.AbstractEventLoop:
        if (
            EventLoopManager._loop is None
            or EventLoopManager._loop.get(server_id) is None
        ):
            raise RuntimeError("Event loop is not set")

        if EventLoopManager._loop.get(server_id).is_closed():
            raise RuntimeError("Event loop is not running")

        return EventLoopManager._loop.get(server_id)

    @staticmethod
    def set_loop(loop: asyncio.AbstractEventLoop, server_id: ServerID) -> None:
        EventLoopManager._loop[server_id] = loop
