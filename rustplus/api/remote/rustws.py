import logging
from threading import Thread
import logging
import websocket
from typing import Optional
from datetime import datetime
import time

from .rustplus_pb2 import AppMessage, AppRequest
from ..structures import RustChatMessage
from ...exceptions import ClientNotConnectedError


class RustWebsocket(websocket.WebSocket):

    def __init__(self, ip, port, remote):

        self.ip = ip
        self.port = port
        self.thread = None
        self.open = False
        self.remote = remote
        self.logger = logging.getLogger("rustplus.py")
        self.connected_time = time.time()

        super().__init__(enable_multithread=True)

    def connect(self, ignore = False) -> None:

        if ((not self.open) or ignore) and not self.remote.is_pending:

            while True:

                self.remote.is_pending = True

                try:
                    super().connect(f"ws://{self.ip}:{self.port}", timeout=7.5)
                    self.connected_time = time.time()
                    break
                except Exception:
                    self.logger.warning(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} [RustPlus.py] Cannot Connect to server. Retrying in 20 seconds")
                    time.sleep(20)

            self.remote.is_pending = False

            self.open = True

            self.thread = Thread(target=self.run, name="[RustPlus.py] WebsocketThread", daemon=True)
            self.thread.start()

    def close(self) -> None:

        super().close()
        self.open = False

    def send_message(self, message : AppRequest) -> None:
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
                    self.logger.warning(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} [RustPlus.py] Connection interrupted, Retrying")
                    self.connect(ignore=True)
                    return
                return

    def handle_message(self, app_message : AppMessage) -> None:

        if app_message.response.seq in self.remote.ignored_responses:
            self.remote.ignored_responses.remove(app_message.response.seq)
            return

        prefix = self.get_prefix(str(app_message.broadcast.teamMessage.message.message))

        if prefix is not None:

            message = RustChatMessage(app_message.broadcast.teamMessage.message)

            self.remote.command_handler.run_command(message, prefix)

        elif self.is_entity_broadcast(app_message):
            self.remote.event_handler.run_entity_event(app_message.broadcast.entityChanged.entityId, app_message)

        elif self.is_team_broadcast(app_message):
            self.remote.event_handler.run_team_event(app_message)

        elif self.is_message(app_message):
            self.remote.event_handler.run_chat_event(app_message)

        else:
            self.remote.responses[app_message.response.seq] = app_message

    def get_prefix(self, message : str) -> Optional[str]:
        if self.remote.use_commands:
            if message.startswith(self.remote.command_options.prefix):
                return self.remote.command_options.prefix

        for overrule in self.remote.command_options.overruling_commands:
            if message.startswith(overrule):
                return overrule

        return None

    def is_message(self, app_message) -> bool:
        return str(app_message.broadcast.teamMessage.message.message) != ""

    def is_entity_broadcast(self, app_message) -> bool:
        return str(app_message.broadcast.entityChanged) != ""

    def is_team_broadcast(self, app_message) -> bool:
        return str(app_message.broadcast.teamChanged) != ""

    async def _retry_failed_request(self, app_request : AppRequest):
        """
        Resends an AppRequest to the server if it has failed
        """
        await self.send_message(app_request)

    def _get_proto_cost(self, app_request) -> int:
        """
        Gets the cost of an AppRequest
        """
        costs = {"getTime" : 1,"sendTeamMessage" : 2,"getInfo" : 1,"getTeamChat" : 1,"getTeamInfo" : 1,"getMapMarkers" : 1,"getMap" : 5,"setEntityValue" : 1,"getEntityInfo" : 1,"promoteToLeader" : 1}
        for request, cost in costs.items():
            if app_request.HasField(request):
                return cost

        raise ValueError()

    def error_present(self, message) -> bool:
        """
        Checks message for error
        """
        return message != ""
