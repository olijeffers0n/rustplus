import asyncio
from asyncio.futures import Future
from datetime import datetime

from . import Command, CommandTime
from ..api.structures import RustChatMessage
from ..commands.command_options import CommandOptions
from ..utils import RegisteredListener


class CommandHandler:
    def __init__(self, command_options: CommandOptions) -> None:
        self.command_options = command_options

    def register_command(self, command, data) -> None:

        if not asyncio.iscoroutinefunction(data[0]):
            raise TypeError("The event registered must be a coroutine")

        setattr(self, command, data)

    def _schedule_event(self, loop, coro, arg) -> None:
        def callback(inner_future: Future):
            inner_future.result()

        future: Future = asyncio.run_coroutine_threadsafe(coro(arg), loop)
        future.add_done_callback(callback)

    def run_command(self, message: RustChatMessage, prefix) -> None:

        if prefix == self.command_options.prefix:
            command = message.message.split(" ")[0][len(prefix) :]
        else:
            command = prefix

        if hasattr(self, command):
            coro, loop = getattr(self, command)

            time = CommandTime(datetime.utcfromtimestamp(message.time), message.time)

            self._schedule_event(
                loop,
                coro,
                Command(
                    message.name,
                    message.steamId,
                    time,
                    command,
                    message.message.split(" ")[1:],
                ),
            )

    def has_command(self, listener: RegisteredListener) -> bool:
        return hasattr(self, listener.listener_id)

    def remove_command(self, listener: RegisteredListener) -> None:
        delattr(self, listener.listener_id)
