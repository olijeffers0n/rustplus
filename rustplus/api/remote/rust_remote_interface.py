import time

from .rustws import RustWsClient
from .event_handler import EventHandler
from .token_bucket import RateLimiter
from ...commands import CommandHandler
from ...exceptions import ClientNotConnectedError

class RustRemote:

    def __init__(self, ip, port, command_options, ratelimit_limit, ratelimit_refill, websocket_length = 600) -> None:

        self.ip = ip
        self.port = port 
        self.command_options = command_options
        self.ratelimit_limit = ratelimit_limit
        self.ratelimit_refill = ratelimit_refill
        self.ratelimiter = RateLimiter(ratelimit_limit, ratelimit_limit, 1, ratelimit_refill)
        self.open = False
        self.websocket_length = websocket_length

        if command_options is None:
            self.use_commands = False
        else:
            self.use_commands = True
            self.command_options = command_options
            self.command_handler = CommandHandler(self.command_options)

        self.event_handler = EventHandler()

    def connect(self) -> None:

        self.ws = RustWsClient(ip=self.ip, port=self.port, remote=self)
        self.ws.daemon = True
        self.ws.connect()
        self.open = True

    def close(self) -> None:

        if self.ws is not None:
            self.ws.close()
            del self.ws
            self.ws = None
            self.open = False

    def sock(self) -> RustWsClient:

        if self.ws is None:
            if not self.open:
                raise ClientNotConnectedError("No Current Websocket Connection")
            else:
                self.connect()

        if time.time() - self.ws.connected_time >= self.websocket_length:
            self.close()
            self.connect()

        if self.ws is None:
            return self.sock()

        return self.ws
