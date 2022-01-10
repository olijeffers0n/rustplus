import time
import asyncio
import logging
from datetime import datetime

from .rustws import RustWsClient
from .rustplus_pb2 import *
from .event_handler import EventHandler
from .token_bucket import RateLimiter
from ...commands import CommandHandler
from ...exceptions import ClientNotConnectedError, ResponseNotRecievedError, RequestError

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
        self.responses = {}
        self.ignored_responses = []

        if command_options is None:
            self.use_commands = False
        else:
            self.use_commands = True
            self.command_options = command_options
            self.command_handler = CommandHandler(self.command_options)

        self.event_handler = EventHandler()

    def connect(self) -> None:

        while True:
            try:
                self.ws = RustWsClient(ip=self.ip, port=self.port, remote=self)
                self.ws.daemon = True
                self.ws.connect()
                self.open = True
                break
            except:
                logging.getLogger("rustplus.py").warn(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} Cannot Connect to server. Retrying in 20 seconds")
                time.sleep(20)

    def close(self) -> None:

        if self.ws is not None:
            self.ws.close()
            self.ws.terminate()
            del self.ws
            self.ws = None
            self.open = False

    async def send_message(self, request : AppRequest) -> None:

        try:
           await self.sock().send_message(request)
        except:
            self.close()
            self.connect()
            return self.send_message(request)

    async def get_response(self, seq : int, app_request : AppRequest, retry_depth : int = 10) -> AppMessage:
        """
        Returns a given response from the server. After 2 seconds throws Exception as response is assumed to not be coming
        """

        attempts = 0
        while seq not in self.responses:

            if attempts == 100:
                if retry_depth != 0:

                    await self.send_message(app_request)
                    return await self.get_response(seq, app_request, retry_depth=retry_depth-1)

                raise ResponseNotRecievedError("Not Recieved")

            attempts += 1
            await asyncio.sleep(0.1)

        response = self.responses.pop(seq)

        if response.response.error.error == "rate_limit":
            logging.getLogger("rustplus.py").warn("[Rustplus.py] RateLimit Exception Occurred. Retrying after bucket is full")

            # Fully Refill the bucket

            self.ratelimiter.last_consumed = time.time()
            self.ratelimiter.bucket.current = 0

            while self.ratelimiter.bucket.current < self.ratelimiter.bucket.max:
                await asyncio.sleep(1)
                self.ratelimiter.bucket.refresh()

            # Reattempt the sending with a full bucket
            cost = self.ws._get_proto_cost(app_request)

            while True:

                if self.ratelimiter.can_consume(cost):
                    self.ratelimiter.consume(cost)
                    break

                await asyncio.sleep(self.ratelimiter.get_estimated_delay_time(cost))

            await self.send_message(app_request)
            response = await self.get_response(seq, app_request, False)
        
        elif self.ws._error_present(response.response.error.error):
            raise RequestError(response.response.error.error)

        return response

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
