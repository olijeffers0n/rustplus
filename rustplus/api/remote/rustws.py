import asyncio
from asyncio import AbstractEventLoop
from typing import Optional
from ws4py.client.threadedclient import WebSocketClient

from rustplus.exceptions.exceptions import ClientNotConnectedError

from .rustplus_pb2 import AppMessage, AppRequest
from .token_bucket import RateLimiter
from ..structures import RustChatMessage
from ...commands import CommandOptions, CommandHandler
from ...exceptions import ResponseNotRecievedError

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

    def is_command(self, app_message) -> bool:
        return self.use_commands and str(app_message.broadcast.teamMessage.message.message).startswith(self.command_options.prefix)

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

    async def get_response(self, seq) -> AppMessage:
        """
        Returns a given response from the server. After 2 seconds throws Exception as response is assumed to not be coming
        """

        attempts = 0
        while seq not in self.responses:

            if attempts == 300:
                raise ResponseNotRecievedError("Not Recieved")

            attempts += 1
            await asyncio.sleep(0.1)

        response = self.responses.pop(seq)

        return response
