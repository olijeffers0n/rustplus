import asyncio
from asyncio import AbstractEventLoop
from ws4py.client.threadedclient import WebSocketClient

from rustplus.exceptions.exceptions import ClientNotConnectedError

from .rustplus_pb2 import AppMessage, AppRequest
from .token_bucket import RateLimiter
from ..structures import RustChatMessage
from ...commands import CommandOptions, CommandHandler
from ...exceptions import ResponseNotRecievedError
class RustWsClient(WebSocketClient):

    def __init__(self, ip, port, command_options : CommandOptions, loop : AbstractEventLoop, protocols=None, extensions=None, heartbeat_freq=None, ssl_options=None, headers=None, exclude_headers=None):
        super().__init__(f"ws://{ip}:{port}", protocols=protocols, extensions=extensions, heartbeat_freq=heartbeat_freq, ssl_options=ssl_options, headers=headers, exclude_headers=exclude_headers)

        self.responses = {}
        self.ignored_responses = []
        self.ratelimiter = None

        if command_options is None:
            self.use_commands = False
        else:
            self.use_commands = True
            self.command_options = command_options
            self.command_handler = CommandHandler(loop, self.command_options)

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

    def received_message(self, message):
        """
        Called when a message is recieved from the server
        """

        app_message = AppMessage()
        app_message.ParseFromString(message.data)

        if app_message.response.seq in self.ignored_responses:
            self.ignored_responses.remove(app_message.response.seq)
            return

        if self.is_command(app_message):

            message = RustChatMessage(app_message.broadcast.teamMessage.message)

            self.command_handler.run_command(message)
            return

        elif self.is_message(app_message):
            return

        self.responses[app_message.response.seq] = app_message

    def is_command(self, app_message) -> bool:
        return self.use_commands and str(app_message.broadcast.teamMessage.message.message).startswith(self.command_options.prefix)

    def is_message(self, app_message) -> bool:
        return str(app_message.broadcast.teamMessage.message.message) != ""

    async def send_message(self, request : AppRequest) -> None:
        """
        Send the Protobuf to the server
        """
        raw_data = request.SerializeToString()

        try:
            self.send(raw_data, binary=True)
        except:
            raise ClientNotConnectedError("Not Connected")

    async def get_response(self, seq) -> AppMessage:
        """
        Returns a given response from the server. After 2 seconds throws Exception as response is assumed to not be coming
        """

        attempts = 0
        while seq not in self.responses:

            if attempts == 50:
                raise ResponseNotRecievedError("Not Recieved")

            attempts += 1
            await asyncio.sleep(0.1)

        response = self.responses.pop(seq)

        return response
