import asyncio
from datetime import datetime

from . import Command, CommandTime
from ..api.structures import RustChatMessage
from ..commands.command_options import CommandOptions
from ..commands.command_data import CommandData
from ..api.remote.events import RegisteredListener


class CommandHandler:
    def __init__(self, command_options: CommandOptions, api) -> None:
        self.command_options = command_options
        self.commands = {}
        self.api = api

    def register_command(self, data: CommandData) -> None:
        if not asyncio.iscoroutinefunction(data.coro):
            raise TypeError("The event registered must be a coroutine")

        self.commands[data.coro.__name__] = data

    async def run_command(self, message: RustChatMessage, prefix) -> None:
        if prefix == self.command_options.prefix:
            command = message.message.split(" ")[0][len(prefix) :]
        else:
            command = prefix

        if command in self.commands:
            data = self.commands[command]

            await data.coro(
                Command(
                    message.name,
                    message.steam_id,
                    CommandTime(datetime.utcfromtimestamp(message.time), message.time),
                    command,
                    message.message.split(" ")[1:],
                )
            )
        else:
            for command_name, data in self.commands.items():
                # Loop through all the commands and see if the command is in the data aliases list
                # or if it matches the callable function

                if command in data.aliases or data.callable_func(command):
                    await data.coro(
                        Command(
                            message.name,
                            message.steam_id,
                            CommandTime(
                                datetime.utcfromtimestamp(message.time), message.time
                            ),
                            command,
                            message.message.split(" ")[1:],
                        ),
                    )
                    break

    def has_command(self, listener: RegisteredListener) -> bool:
        return listener.listener_id in self.commands

    def remove_command(self, listener: RegisteredListener) -> None:
        try:
            del self.commands[listener.listener_id]
        except KeyError:
            pass
