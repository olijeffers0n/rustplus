import asyncio
from datetime import datetime

from . import Command, CommandTime
from ..api.structures import RustChatMessage
from ..commands.command_options import CommandOptions

class CommandHandler:

    def __init__(self, command_options : CommandOptions) -> None:
        self.command_options = command_options

    def registerCommand(self, command, coro, loop) -> None:
        
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError("The event registered must be a coroutine")

        setattr(self, command, (coro, loop))

    def _schedule_event(self, loop, coro, arg) -> None:
        asyncio.run_coroutine_threadsafe(coro(arg), loop)

    def run_command(self, message : RustChatMessage, prefix) -> None:

        if prefix == self.command_options.prefix:
            command = message.message.split(" ")[0][len(prefix):]
        else:
            command = prefix

        if hasattr(self, command):
            coro, loop = getattr(self, command)

            time = CommandTime(datetime.utcfromtimestamp(message.time), message.time)

            self._schedule_event(loop, coro, Command(message.name, message.steamId, time, command, message.message.split(" ")[1:]))
