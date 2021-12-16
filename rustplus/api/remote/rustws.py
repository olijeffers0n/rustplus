import asyncio
from ws4py.client.threadedclient import WebSocketClient

from .rustproto import AppMessage, AppRequest
from .token_bucket import RateLimiter

class RustWsClient(WebSocketClient):

    def __init__(self, ip, port, protocols=None, extensions=None, heartbeat_freq=None, ssl_options=None, headers=None, exclude_headers=None):
        super().__init__(f"ws://{ip}:{port}", protocols=protocols, extensions=extensions, heartbeat_freq=heartbeat_freq, ssl_options=ssl_options, headers=headers, exclude_headers=exclude_headers)

        self.responses = {}
        self.ratelimiter = None

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

        self.responses[app_message.response.seq] = app_message

    async def send_message(self, request : AppRequest) -> None:
        """
        Send the Protobuf to the server
        """
        raw_data = request.SerializeToString()

        self.send(raw_data, binary=True)

    async def get_response(self, seq) -> AppMessage:
        """
        Returns a given response from the server. After 2 seconds throws Exception as response is assumed to not be coming
        """

        attempts = 0
        while seq not in self.responses:

            if attempts == 20:
                raise Exception("Not Recieved")

            attempts += 1
            await asyncio.sleep(0.1)

        response = self.responses.pop(seq)

        return response




