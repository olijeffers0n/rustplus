import logging
import time
import socket
import errno
from typing import Optional
from ws4py.client.threadedclient import WebSocketClient
from ws4py.websocket import pyOpenSSLError

from .rustplus_pb2 import AppMessage, AppRequest
from ..structures import RustChatMessage

class RustWsClient(WebSocketClient):

    def __init__(self, ip, port, remote, protocols=None, extensions=None, heartbeat_freq=None, ssl_options=None, headers=None, exclude_headers=None):
        super().__init__(f"ws://{ip}:{port}", protocols=protocols, extensions=extensions, heartbeat_freq=heartbeat_freq, ssl_options=ssl_options, headers=headers, exclude_headers=exclude_headers)

        self.remote = remote
        self.connected_time = time.time()

    def opened(self): 
        """
        Called when the connection is opened
        """
        return 

    def closed(self, code, reason):
        """
        Called when the connection is closed
        """
        self.remote.ws = None
        return

    def connect(self) -> None:

        super().connect()
        self.client_terminated = False
        self.server_terminated = False

    def close(self, code=1000, reason='') -> None:
        super().close(code=code, reason=reason)

    def received_message(self, message):
        """
        Called when a message is recieved from the server
        """

        app_message = AppMessage()
        app_message.ParseFromString(message.data)

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

    async def send_message(self, request : AppRequest) -> None:
        """
        Send the Protobuf to the server
        """
        raw_data = request.SerializeToString()

        self.send(raw_data, binary=True)

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

    def _error_present(self, message) -> bool:
        """
        Checks message for error
        """
        return message != ""

    def once(self):

        if self.terminated:
            logging.getLogger("ws4py").debug("WebSocket is already terminated")
            return False
        try:
            b = b''
            if self._is_secure:
                b = self._get_from_pending()
            if not b and not self.buf:
                try:
                    b = self.sock.recv(self.reading_buffer_size)
                except OSError:
                    self.close()
                    self.terminate()
                    self.remote.connect()
                    return True
            if not b and not self.buf:
                return False
            self.buf += b
        except (socket.error, OSError, pyOpenSSLError) as e:
            if hasattr(e, "errno") and e.errno == errno.EINTR:
                pass
            else:
                self.unhandled_error(e)
                return False
        else:
            # process as much as we can
            # the process will stop either if there is no buffer left
            # or if the stream is closed
            # only pass the requested number of bytes, leave the rest in the buffer
            requested = self.reading_buffer_size
            if not self.process(self.buf[:requested]):
                return False
            self.buf = self.buf[requested:]

        return True
