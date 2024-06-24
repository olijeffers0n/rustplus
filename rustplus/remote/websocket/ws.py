import shlex
import betterproto
from websockets.exceptions import InvalidURI, InvalidHandshake
from websockets.legacy.client import WebSocketClientProtocol
from websockets.client import connect
from asyncio import TimeoutError, Task, AbstractEventLoop
from typing import Union, Coroutine, Optional, Set, Dict
import logging
import asyncio

from ..rustplus_proto import AppMessage, AppRequest
from ...commands import CommandOptions, ChatCommand, ChatCommandTime
from ...exceptions import ClientNotConnectedError, RequestError
from ...identification import ServerID
from ...structs import RustChatMessage
from ...utils import YieldingEvent, convert_time


class RustWebsocket:
    def __init__(self, server_id: ServerID, command_options: Union[None, CommandOptions]) -> None:
        self.server_id: ServerID = server_id
        self.command_options: Union[None, CommandOptions] = command_options
        self.connection: Union[WebSocketClientProtocol, None] = None
        self.logger: logging.Logger = logging.getLogger("rustplus.py")
        self.task: Union[Task, None] = None
        self.debug: bool = True
        self.use_test_server: bool = False

        self.responses: Dict[int, YieldingEvent] = {}

    async def connect(self) -> bool:

        address = "ws://" + self.server_id.get_server_string()

        try:
            self.connection = await connect(
                address,
                close_timeout=0,
                ping_interval=None,
                max_size=1_000_000_000,
            )
        except (InvalidURI, OSError, InvalidHandshake, TimeoutError) as err:
            self.logger.warning("WebSocket connection error: %s", err)
            return False

        self.logger.info("Websocket connection established to %s", address)

        self.task = asyncio.create_task(
            self.run(), name="[RustPlus.py] Websocket Polling Task"
        )

        return True

    async def run(self) -> None:
        while True:
            try:
                data = await self.connection.recv()

                # TODO
                # await self.run_coroutine_non_blocking(
                #     EventHandler.run_proto_event(data, self.server_id)
                # )

                app_message = AppMessage()
                app_message.parse(data)

            except Exception as e:
                continue

            try:
                await self.run_coroutine_non_blocking(self.handle_message(app_message))
            except Exception as e:
                print(e)
                self.logger.exception(
                    "An Error occurred whilst handling the message from the server"
                )

    async def send_and_get(self, request: AppRequest) -> AppMessage:
        await self.send_message(request)
        return await self.get_response(request)

    async def send_message(self, request: AppRequest, ignore_response: bool = False) -> None:
        if self.connection is None:
            raise ClientNotConnectedError("No Current Websocket Connection")

        if self.debug:
            self.logger.info(
                f"Sending Message with seq {request.seq}: {request}"
            )

        if not ignore_response:
            self.responses[request.seq] = YieldingEvent()

        try:
            await self.connection.send(bytes(request))
        except Exception as err:
            self.logger.warning("WebSocket connection error: %s", err)

    async def get_response(self, request: AppRequest) -> AppMessage:

        response = await self.responses[request.seq].wait()
        del self.responses[request.seq]

        return response

    async def handle_message(self, app_message: AppMessage) -> None:
        if self.debug:
            self.logger.info(
                f"Received Message with seq {app_message.response.seq}: {app_message}"
            )

        if self.error_present(app_message.response.error.error):
            raise RequestError(app_message.response.error.error)

        prefix = self.get_prefix(
            str(app_message.broadcast.team_message.message.message)
        )

        if prefix is not None:
            # This means it is a command

            if self.debug:
                self.logger.info(
                    f"Attempting to run Command: {app_message}"
                )

            message = RustChatMessage(app_message.broadcast.team_message.message)

            parts = shlex.split(message.message)
            command = parts[0][len(prefix) :]

            data = ChatCommand.REGISTERED_COMMANDS[self.server_id].get(command, None)

            dao = ChatCommand(
                message.name,
                message.steam_id,
                ChatCommandTime(
                    convert_time(message.time),
                    message.time,
                ),
                command,
                parts[1:],
            )

            if data is not None:
                await data.coroutine(dao)
            else:
                for command_name, data in ChatCommand.REGISTERED_COMMANDS[
                    self.server_id
                ].items():
                    if (
                        command in data.aliases
                        or data.callable_func(command)
                    ):
                        await data.coroutine(dao)
                        break

        if self.is_entity_broadcast(app_message):
            # This means that an entity has changed state

            if self.debug:
                self.logger.info(f"Running Entity Event: {app_message}")

            # TODO
            # await EventHandler.run_entity_event(
            #     app_message.broadcast.entity_changed.entity_id,
            #     app_message,
            #     self.server_id,
            # )

        elif self.is_camera_broadcast(app_message):
            if self.debug:
                self.logger.info(f"Running Camera Event: {app_message}")

            # TODO
            # if self.remote.camera_manager is not None:
            #     await self.remote.camera_manager.add_packet(
            #         RayPacket(app_message.broadcast.camera_rays)
            #     )

        elif self.is_team_broadcast(app_message):
            if self.debug:
                self.logger.info(f"Running Team Event: {app_message}")

            # This means that the team of the current player has changed
            # TODO await EventHandler.run_team_event(app_message, self.server_id)

        elif self.is_message(app_message):
            # This means that a message has been sent to the team chat

            if self.debug:
                self.logger.info(f"Running Chat Event: {app_message}")

            steam_id = int(app_message.broadcast.team_message.message.steam_id)
            message = str(app_message.broadcast.team_message.message.message)

            # TODO await EventHandler.run_chat_event(app_message, self.server_id)

        else:
            # This means that it wasn't sent by the server and is a message from the server in response to an action
            event: YieldingEvent = self.responses.get(app_message.response.seq, None)
            if event is not None:
                if self.debug:
                    self.logger.info(
                        f"Running Response Event: {app_message}"
                    )

                event.set_with_value(app_message)

    def get_prefix(self, message: str) -> Optional[str]:

        if self.command_options is None:
            return None

        if message.startswith(self.command_options.prefix):
            return self.command_options.prefix
        else:
            return None

    @staticmethod
    def is_message(app_message: AppMessage) -> bool:
        return betterproto.serialized_on_wire(
            app_message.broadcast.team_message.message
        )

    @staticmethod
    def is_camera_broadcast(app_message: AppMessage) -> bool:
        return betterproto.serialized_on_wire(app_message.broadcast.camera_rays)

    @staticmethod
    def is_entity_broadcast(app_message: AppMessage) -> bool:
        return betterproto.serialized_on_wire(app_message.broadcast.entity_changed)

    @staticmethod
    def is_team_broadcast(app_message: AppMessage) -> bool:
        return betterproto.serialized_on_wire(app_message.broadcast.team_changed)

    @staticmethod
    def get_proto_cost(app_request: AppRequest) -> int:
        """
        Gets the cost of an AppRequest
        """
        costs = [
            (app_request.get_time, 1),
            (app_request.send_team_message, 2),
            (app_request.get_info, 1),
            (app_request.get_team_chat, 1),
            (app_request.get_team_info, 1),
            (app_request.get_map_markers, 1),
            (app_request.get_map, 5),
            (app_request.set_entity_value, 1),
            (app_request.get_entity_info, 1),
            (app_request.promote_to_leader, 1),
        ]
        for request, cost in costs:
            if betterproto.serialized_on_wire(request):
                return cost

        raise ValueError()

    @staticmethod
    def error_present(message) -> bool:
        """
        Checks message for error
        """
        return message != ""

    @staticmethod
    async def run_coroutine_non_blocking(coroutine: Coroutine) -> Task:
        loop: AbstractEventLoop = asyncio.get_event_loop_policy().get_event_loop()
        return loop.create_task(coroutine)
