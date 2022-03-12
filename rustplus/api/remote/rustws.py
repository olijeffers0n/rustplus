import logging
import time
from datetime import datetime
from threading import Thread
from typing import Optional
import websocket

from .rustplus_pb2 import AppMessage, AppRequest
from ..structures import RustChatMessage
from ...exceptions import ClientNotConnectedError


class RustWebsocket(websocket.WebSocket):
    def __init__(self, ip, port, remote, use_proxy):

        self.ip = ip
        self.port = port
        self.thread = None
        self.open = False
        self.use_proxy = use_proxy
        self.remote = remote
        self.logger = logging.getLogger("rustplus.py")
        self.connected_time = time.time()

        super().__init__(enable_multithread=True)

    def connect(self, retries = float("inf"), ignore=False) -> None:

        if ((not self.open) or ignore) and not self.remote.is_pending:

            attempts = 0

            while True:

                if attempts >= retries:
                    raise ConnectionAbortedError("Reached Retry Limit")

                self.remote.is_pending = True

                try:
                    address = (
                        f"wss://companion-rust.facepunch.com/game/{self.ip}/{self.port}"
                        if self.use_proxy
                        else f"ws://{self.ip}:{self.port} "
                    )
                    super().connect(address)
                    self.connected_time = time.time()
                    break
                except Exception:
                    self.logger.warning(
                        f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} "
                        "[RustPlus.py] Cannot Connect to server. Retrying in 20 seconds"
                    )
                    attempts += 1
                    time.sleep(20)

            self.remote.is_pending = False

            self.open = True

            self.thread = Thread(
                target=self.run, name="[RustPlus.py] WebsocketThread", daemon=True
            )
            self.thread.start()

    def close(self) -> None:

        super().close()
        self.open = False

    def send_message(self, message: AppRequest) -> None:
        """
        Send the Protobuf to the server
        """
        try:
            self.remote.pending_requests[message.seq] = message
            self.send_binary(message.SerializeToString())
        except Exception:
            if not self.open:
                raise ClientNotConnectedError("Not Connected")

    def run(self) -> None:

        while self.open:
            try:
                data = self.recv()
                app_message = AppMessage()
                app_message.ParseFromString(data)

                try:
                    del self.remote.pending_requests[app_message.response.seq]
                except KeyError:
                    pass

                self.handle_message(app_message)

            except Exception:
                if self.open:
                    self.logger.warning(
                        f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} [RustPlus.py] Connection interrupted, Retrying"
                    )
                    self.connect(ignore=True)
                    return
                return

    def handle_message(self, app_message: AppMessage) -> None:

        if app_message.response.seq in self.remote.ignored_responses:
            self.remote.ignored_responses.remove(app_message.response.seq)
            return

        prefix = self.get_prefix(str(app_message.broadcast.teamMessage.message.message))

        if prefix is not None:

            message = RustChatMessage(app_message.broadcast.teamMessage.message)

            self.remote.command_handler.run_command(message, prefix)

        elif self.is_entity_broadcast(app_message):
            self.remote.event_handler.run_entity_event(
                app_message.broadcast.entityChanged.entityId, app_message
            )

        elif self.is_team_broadcast(app_message):
            self.remote.event_handler.run_team_event(app_message)

        elif self.is_message(app_message):
            self.remote.event_handler.run_chat_event(app_message)

        else:
            self.remote.responses[app_message.response.seq] = app_message

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
    def is_message(app_message) -> bool:
        return str(app_message.broadcast.teamMessage.message.message) != ""

    @staticmethod
    def is_entity_broadcast(app_message) -> bool:
        return str(app_message.broadcast.entityChanged) != ""

    @staticmethod
    def is_team_broadcast(app_message) -> bool:
        return str(app_message.broadcast.teamChanged) != ""

    async def _retry_failed_request(self, app_request: AppRequest):
        """
        Resends an AppRequest to the server if it has failed
        """
        await self.send_message(app_request)

    @staticmethod
    def _get_proto_cost(app_request) -> int:
        """
        Gets the cost of an AppRequest
        """
        costs = {
            "getTime": 1,
            "sendTeamMessage": 2,
            "getInfo": 1,
            "getTeamChat": 1,
            "getTeamInfo": 1,
            "getMapMarkers": 1,
            "getMap": 5,
            "setEntityValue": 1,
            "getEntityInfo": 1,
            "promoteToLeader": 1,
        }
        for request, cost in costs.items():
            if app_request.HasField(request):
                return cost

        raise ValueError()

    @staticmethod
    def error_present(message) -> bool:
        """
        Checks message for error
        """
        return message != ""
