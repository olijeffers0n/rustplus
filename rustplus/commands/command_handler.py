import asyncio
from asyncio import AbstractEventLoop
from datetime import datetime

from . import CommandOptions
from . import Command, CommandTime
from ..api.structures import RustChatMessage

class CommandHandler:

    def __init__(self, loop : AbstractEventLoop, options : CommandOptions) -> None:
        self.prefix = options.prefix
        self.loop = loop

    def registerCommand(self, command, coro) -> None:
        
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError("The event registered must be a coroutine")

        setattr(self, command, coro)

    def _schedule_event(self, coro, arg) -> None:
        asyncio.run_coroutine_threadsafe(coro(arg), self.loop)

    def run_command(self, message : RustChatMessage) -> None:

        command = message.message.split(" ")[0][len(self.prefix):]

        if hasattr(self, command):
            coro = getattr(self, command)

            time = CommandTime(datetime.utcfromtimestamp(message.time), message.time)

            self._schedule_event(coro, Command(message.name, message.steamId, time, command, message.message.split(" ")[1:]))
