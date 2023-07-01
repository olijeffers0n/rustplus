import asyncio
import base64
import logging
import time
from datetime import datetime
from typing import Optional, Union, Coroutine
import betterproto
from asyncio import Task, AbstractEventLoop
from websockets.client import connect
from websockets.legacy.client import WebSocketClientProtocol

from .camera.structures import RayPacket
from .rustplus_proto import AppMessage, AppRequest
from .events import EventHandler
from ..structures import RustChatMessage
from ...exceptions import ClientNotConnectedError
from ...conversation import Conversation
from ...utils import ServerID, YieldingEvent

CONNECTED = 1
PENDING_CONNECTION = 2
CLOSING = 4
CLOSED = 3


class RustWebsocket:
    def __init__(
        self,
        server_id: ServerID,
        remote,
        use_proxy,
        magic_value,
        use_test_server,
        on_failure,
        on_success,
        delay,
    ):
        self.connection: Union[WebSocketClientProtocol, None] = None
        self.task: Union[Task, None] = None
        self.server_id = server_id
        self.connection_status = CLOSED
        self.use_proxy = use_proxy
        self.remote = remote
        self.logger = logging.getLogger("rustplus.py")
        self.connected_time = time.time()
        self.magic_value = magic_value
        self.use_test_server = use_test_server
        self.outgoing_conversation_messages = []
        self.on_failure = on_failure
        self.on_success = on_success
        self.delay = delay

    async def connect(
        self, retries=float("inf"), ignore_open_value: bool = False
    ) -> None:
        if (
            not self.connection_status == CONNECTED or ignore_open_value
        ) and not self.remote.is_pending():
            attempts = 0

            while True:
                if attempts >= retries:
                    raise ConnectionAbortedError("Reached Retry Limit")

                self.connection_status = PENDING_CONNECTION

                try:
                    address = (
                        (
                            f"wss://{self.server_id.ip}"
                            if self.server_id.port is None
                            else f"ws://{self.server_id.ip}:{self.server_id.port}"
                        )
                        if self.use_test_server
                        else (
                            f"wss://companion-rust.facepunch.com/game/{self.server_id.ip}/{self.server_id.port}"
                            if self.use_proxy
                            else f"ws://{self.server_id.ip}:{self.server_id.port}"
                        )
                    )
                    address += f"?v={str(self.magic_value)}"
                    self.connection = await connect(
                        address, close_timeout=0, ping_interval=None
                    )
                    self.connected_time = time.time()

                    if self.on_success is not None:
                        try:
                            if asyncio.iscoroutinefunction(self.on_success):
                                await self.on_success()
                            else:
                                self.on_success()
                        except Exception as e:
                            self.logger.warning(e)
                    break

                except Exception as exception:
                    print_error = True

                    if not isinstance(exception, KeyboardInterrupt):
                        # Run the failure callback
                        if self.on_failure is not None:
                            try:
                                if asyncio.iscoroutinefunction(self.on_failure):
                                    val = await self.on_failure()
                                else:
                                    val = self.on_failure()

                                if val is not None:
                                    print_error = val

                            except Exception as e:
                                self.logger.warning(e)

                    if print_error:
                        self.logger.warning(
                            f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} "
                            f"[RustPlus.py] Cannot Connect to server. Retrying in {str(self.delay)} second/s"
                        )
                    attempts += 1
                    await asyncio.sleep(self.delay)

            self.connection_status = CONNECTED

        if not ignore_open_value:
            self.task = asyncio.create_task(
                self.run(), name="[RustPlus.py] Websocket Polling Task"
            )

    async def close(self) -> None:
        self.connection_status = CLOSING
        await self.connection.close()
        self.connection = None
        self.task.cancel()
        self.task = None
        self.connection_status = CLOSED

    async def send_message(self, message: AppRequest) -> None:
        """
        Send the Protobuf to the server
        """

        if self.connection_status == CLOSED:
            raise ClientNotConnectedError("Not Connected")

        try:
            if self.use_test_server:
                await self.connection.send(
                    base64.b64encode(bytes(message)).decode("utf-8")
                )
            else:
                await self.connection.send(bytes(message))
        except Exception:
            self.logger.exception("An exception occurred whilst sending a message")

            while self.remote.is_pending():
                await asyncio.sleep(0.5)
            return await self.send_message(message)

    async def run(self) -> None:
        while self.connection_status == CONNECTED:
            try:
                data = await self.connection.recv()

                # See below for context on why this is needed
                await self.run_coroutine_non_blocking(
                    EventHandler.run_proto_event(data, self.server_id)
                )

                app_message = AppMessage()
                app_message.parse(
                    base64.b64decode(data) if self.use_test_server else data
                )

            except Exception as e:
                if self.connection_status == CONNECTED:
                    print(e)
                    self.logger.exception(
                        f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} [RustPlus.py] Connection interrupted, Retrying"
                    )
                    await self.connect(ignore_open_value=True)

                    continue
                return

            try:
                # This creates an asyncio task rather than awaiting the coroutine directly.
                # This fixes the bug where if you called a BaseRustSocket#get... from within a RegisteredListener or callback,
                # It would hang the websocket. This is because the websocket event loop would be stuck on the callback rather than polling the socket.
                # This way, we can schedule the execution of all logic for this message, but continue polling the WS
                await self.run_coroutine_non_blocking(self.handle_message(app_message))
            except Exception:
                self.logger.exception(
                    "An Error occurred whilst handling the message from the server"
                )

    async def handle_message(self, app_message: AppMessage) -> None:
        if app_message.response.seq in self.remote.ignored_responses:
            self.remote.ignored_responses.remove(app_message.response.seq)
            return

        prefix = self.get_prefix(
            str(app_message.broadcast.team_message.message.message)
        )

        if prefix is not None:
            # This means it is a command

            message = RustChatMessage(app_message.broadcast.team_message.message)
            await self.remote.command_handler.run_command(message, prefix)

        if self.is_entity_broadcast(app_message):
            # This means that an entity has changed state

            await EventHandler.run_entity_event(
                app_message.broadcast.entity_changed.entity_id,
                app_message,
                self.server_id,
            )

        elif self.is_camera_broadcast(app_message):
            if self.remote.camera_manager is not None:
                await self.remote.camera_manager.add_packet(
                    RayPacket(app_message.broadcast.camera_rays)
                )

        elif self.is_team_broadcast(app_message):
            # This means that the team of the current player has changed
            await EventHandler.run_team_event(app_message, self.server_id)

        elif self.is_message(app_message):
            # This means that a message has been sent to the team chat

            steam_id = int(app_message.broadcast.team_message.message.steam_id)
            message = str(app_message.broadcast.team_message.message.message)

            # Conversation API
            if self.remote.conversation_factory.has_conversation(steam_id):
                if message not in self.outgoing_conversation_messages:
                    conversation: Conversation = (
                        self.remote.conversation_factory.get_conversation(steam_id)
                    )

                    conversation.get_answers().append(message)
                    await conversation.get_current_prompt().on_response(message)

                    if conversation.has_next():
                        conversation.increment_prompt()
                        prompt = conversation.get_current_prompt()
                        prompt_string = await prompt.prompt()
                        await conversation.send_prompt(prompt_string)

                    else:
                        prompt = conversation.get_current_prompt()
                        prompt_string = await prompt.on_finish()
                        if prompt_string != "":
                            await conversation.send_prompt(prompt_string)
                        self.remote.conversation_factory.abort_conversation(steam_id)
                else:
                    self.outgoing_conversation_messages.remove(message)

                # Conversation API end

            await EventHandler.run_chat_event(app_message, self.server_id)

        else:
            # This means that it wasn't sent by the server and is a message from the server in response to an action
            event: YieldingEvent = self.remote.pending_response_events[
                app_message.response.seq
            ]
            event.set_with_value(app_message)

    def get_prefix(self, message: str) -> Optional[str]:
        if self.remote.use_commands:
            if message.startswith(self.remote.command_options.prefix):
                return self.remote.command_options.prefix
        else:
            return None

        for overrule in self.remote.command_options.overruling_commands:
            if message.startswith(overrule):
                return overrule

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
