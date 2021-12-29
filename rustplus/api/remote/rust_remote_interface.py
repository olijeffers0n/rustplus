from typing import Optional
from .rustws import RustWsClient
from .token_bucket import RateLimiter
from ...commands import CommandHandler
from ...exceptions import ClientNotConnectedError

class RustRemote:

    def __init__(self, ip, port, command_options, ratelimit_limit, ratelimit_refill) -> None:

        self.ip = ip
        self.port = port 
        self.command_options = command_options
        self.ratelimit_limit = ratelimit_limit
        self.ratelimit_refill = ratelimit_refill
        self.ratelimiter = RateLimiter(ratelimit_limit, ratelimit_limit, 1, ratelimit_refill)

        if command_options is None:
            self.use_commands = False
        else:
            self.use_commands = True
            self.command_options = command_options
            self.command_handler = CommandHandler(self.command_options)

    def connect(self) -> None:

        self.ws = RustWsClient(ip=self.ip, port=self.port, remote=self, protocols=['http-only', 'chat'])
        self.ws.daemon = True
        self.ws.connect()

    def close(self) -> None:

        if self.ws:
            self.ws.close()
            self.ws = None

    def sock(self) -> RustWsClient:

        if self.ws is None:
            raise ClientNotConnectedError("No Current Websocket Connection")

        return self.ws
