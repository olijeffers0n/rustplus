import asyncio
import logging
import time
from typing import Optional
from ws4py.client.threadedclient import WebSocketClient

from .rustplus_pb2 import AppMessage, AppRequest
from ..structures import RustChatMessage
from ...exceptions import ResponseNotRecievedError, ClientNotConnectedError, RequestError

class RustWsClient(WebSocketClient):

    def __init__(self, ip, port, remote, protocols=None, extensions=None, heartbeat_freq=None, ssl_options=None, headers=None, exclude_headers=None):
        super().__init__(f"ws://{ip}:{port}", protocols=protocols, extensions=extensions, heartbeat_freq=heartbeat_freq, ssl_options=ssl_options, headers=headers, exclude_headers=exclude_headers)

        self.responses = {}
        self.ignored_responses = []
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

        try:
            super().connect()
            self.client_terminated = False
            self.server_terminated = False
        except OSError:
            raise ConnectionRefusedError()

    def close(self, code=1000, reason='') -> None:
        super().close(code=code, reason=reason)

    def received_message(self, message):
        """
        Called when a message is recieved from the server
        """

        app_message = AppMessage()
        app_message.ParseFromString(message.data)

        if app_message.response.seq in self.ignored_responses:
            self.ignored_responses.remove(app_message.response.seq)
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
            self.responses[app_message.response.seq] = app_message

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

        try:
            self.send(raw_data, binary=True)
        except:
            raise ClientNotConnectedError("Not Connected")

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

    async def get_response(self, seq : int, app_request : AppRequest, retry_depth : int = 10) -> AppMessage:
        """
        Returns a given response from the server. After 2 seconds throws Exception as response is assumed to not be coming
        """

        attempts = 0
        while seq not in self.responses:

            if attempts == 100:
                if retry_depth != 0:

                    await self._retry_failed_request(app_request)
                    return await self.get_response(seq, app_request, retry_depth=retry_depth-1)

                raise ResponseNotRecievedError("Not Recieved")

            attempts += 1
            await asyncio.sleep(0.1)

        response = self.responses.pop(seq)

        if response.response.error.error == "rate_limit":
            logging.getLogger("rustplus.py").warn("[Rustplus.py] RateLimit Exception Occurred. Retrying after bucket is full")

            # Fully Refill the bucket

            self.remote.ratelimiter.last_consumed = time.time()
            self.remote.ratelimiter.bucket.current = 0

            while self.remote.ratelimiter.bucket.current < self.remote.ratelimiter.bucket.max:
                await asyncio.sleep(1)
                self.remote.ratelimiter.bucket.refresh()

            # Reattempt the sending with a full bucket
            cost = self._get_proto_cost(app_request)

            while True:

                if self.remote.ratelimiter.can_consume(cost):
                    self.remote.ratelimiter.consume(cost)
                    break

                await asyncio.sleep(self.remote.ratelimiter.get_estimated_delay_time(cost))

            await self._retry_failed_request(app_request)
            response = await self.get_response(seq, app_request, False)
        
        elif self._error_present(response.response.error.error):
            raise RequestError(response.response.error.error)

        return response
