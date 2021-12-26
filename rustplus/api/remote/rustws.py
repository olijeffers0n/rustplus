import asyncio
import logging
from typing import Optional
from ws4py.client.threadedclient import WebSocketClient

from .rustplus_pb2 import AppMessage, AppRequest
from .token_bucket import RateLimiter
from ..structures import RustChatMessage
from ...commands import CommandOptions, CommandHandler
from ...exceptions import ResponseNotRecievedError, ClientNotConnectedError, RequestError

class RustWsClient(WebSocketClient):

    def __init__(self, ip, port, command_options : CommandOptions, protocols=None, extensions=None, heartbeat_freq=None, ssl_options=None, headers=None, exclude_headers=None):
        super().__init__(f"ws://{ip}:{port}", protocols=protocols, extensions=extensions, heartbeat_freq=heartbeat_freq, ssl_options=ssl_options, headers=headers, exclude_headers=exclude_headers)

        self.responses = {}
        self.ignored_responses = []
        self.ratelimiter = None
        self.open = False

        if command_options is None:
            self.use_commands = False
        else:
            self.use_commands = True
            self.command_options = command_options
            self.command_handler = CommandHandler(self.command_options)

    def start_ratelimiter(self, current, max, refresh_rate, refresh_amount) -> None:

        self.ratelimiter = RateLimiter(current, max, refresh_rate, refresh_amount)

    def opened(self): 
        """
        Called when the connection is opened
        """
        return 

    def closed(self, code, reason):
        """
        Called when the connection is closed
        """
        return

    def connect(self) -> None:

        try:
            super().connect()
        except OSError:
            pass

        self.open = True

    def close(self, code=1000, reason='') -> None:
        super().close(code=code, reason=reason)
        self.open = False

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

            self.command_handler.run_command(message, prefix)
            return

        elif self.is_message(app_message):
            return

        self.responses[app_message.response.seq] = app_message

    def get_prefix(self, message : str) -> Optional[str]:
        if message.startswith(self.command_options.prefix):
            return self.command_options.prefix
        
        for overrule in self.command_options.overruling_commands:
            if message.startswith(overrule):
                return overrule

        return None

    def is_message(self, app_message) -> bool:
        return str(app_message.broadcast.teamMessage.message.message) != ""

    async def send_message(self, request : AppRequest, depth = 1) -> None:
        """
        Send the Protobuf to the server
        """
        raw_data = request.SerializeToString()

        try:
            self.send(raw_data, binary=True)
        except:
            if not self.open or depth >= 10:
                raise ClientNotConnectedError("Not Connected")
            self.close()
            self.connect()
            await self.send_message(request=request, depth=depth + 1)

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

    async def get_response(self, seq : int, app_request : AppRequest, attempt_retry : bool = True) -> AppMessage:
        """
        Returns a given response from the server. After 2 seconds throws Exception as response is assumed to not be coming
        """

        attempts = 0
        while seq not in self.responses:

            if attempts == 100:
                if attempt_retry:

                    await self._retry_failed_request(app_request)
                    return await self.get_response(seq, app_request, False)

                raise ResponseNotRecievedError("Not Recieved")

            attempts += 1
            await asyncio.sleep(0.1)

        response = self.responses.pop(seq)

        if response.response.error.error == "rate_limit":
            logging.getLogger("rustplus.py").warn("[Rustplus.py] RateLimit Exception Occurred. Retrying after bucket is full")

            # Fully Refill the bucket
            while self.ratelimiter.bucket.current < self.ratelimiter.bucket.max:
                await asyncio.sleep(1)
                self.ratelimiter.bucket.refresh()

            # Reattempt the sending with a full bucket
            cost = self._get_proto_cost(app_request)

            while True:

                if self.ratelimiter.can_consume(cost):
                    self.ratelimiter.consume(cost)
                    break

                await asyncio.sleep(self.ratelimiter.get_estimated_delay_time(cost))

            await self._retry_failed_request(app_request)
            response = await self.get_response(seq, app_request, False)
        
        elif self._error_present(response.response.error.error):
            raise RequestError(response.response.error.error)

        return response
