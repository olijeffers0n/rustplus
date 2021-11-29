import asyncio

from rustplus import commands, exceptions

from ..api.structures import RustChatMessage
from .command_options import CommandOptions
from .command import Command

class RustCommandHandler:

    def __init__(self, options : CommandOptions) -> None:
        self.prefix = options.prefix

    def register_command(self, target, coro) -> None:

        if not asyncio.iscoroutinefunction(coro):
            raise TypeError("The event registered must be a coroutine")

        setattr(self, target, coro)

    async def run_command(self, message : RustChatMessage) -> None:

        command = message.message.split(" ")[0][len(self.prefix):]

        if hasattr(self, command):
            
            coro = getattr(self, command)

            await coro(Command(message.name, message.steamId, message.message, message.time))
