import asyncio
import logging
import time

from rustplus.api.remote.events.event_handler import EventHandler
from .rustplus_proto import AppRequest, AppMessage
from .events import ChatEvent, TeamEvent, EntityEvent, ProtobufEvent
from .rustws import RustWebsocket, CONNECTED, PENDING_CONNECTION
from .token_bucket import RateLimiter
from .expo_bundle_handler import MagicValueGrabber
from ...conversation import ConversationFactory
from ...commands import CommandHandler
from ...exceptions import (
    ClientNotConnectedError,
    ResponseNotReceivedError,
    RequestError,
)
from ..remote.events import RegisteredListener


class RustRemote:
    def __init__(
        self,
        ip,
        port,
        command_options,
        ratelimit_limit,
        ratelimit_refill,
        websocket_length=600,
        use_proxy: bool = False,
        api=None,
        loop=None,
        use_test_server: bool = False,
    ) -> None:

        self.ip = ip
        self.port = port
        self.command_options = command_options
        self.ratelimit_limit = ratelimit_limit
        self.ratelimit_refill = ratelimit_refill
        self.use_proxy = use_proxy
        self.ratelimiter = RateLimiter(
            ratelimit_limit, ratelimit_limit, 1, ratelimit_refill
        )
        self.ws = None
        self.websocket_length = websocket_length
        self.responses = {}
        self.ignored_responses = []
        self.pending_for_response = {}
        self.sent_requests = []
        self.command_handler = None

        if command_options is None:
            self.use_commands = False
        else:
            self.use_commands = True
            self.command_handler = CommandHandler(self.command_options)

        self.event_handler = EventHandler()

        self.magic_value = MagicValueGrabber.get_magic_value()
        self.conversation_factory = ConversationFactory(api)
        self.loop = loop
        self.use_test_server = use_test_server

    async def connect(self, retries, delay, on_failure=None) -> None:

        self.ws = RustWebsocket(
            ip=self.ip,
            port=self.port,
            remote=self,
            use_proxy=self.use_proxy,
            magic_value=self.magic_value,
            use_test_server=self.use_test_server,
            on_failure=on_failure,
            delay=delay,
            loop=asyncio.get_event_loop_policy().get_event_loop(),
        )
        await self.ws.connect(retries=retries)

    def close(self) -> None:

        if self.ws is not None:
            self.ws.close()
            del self.ws
            self.ws = None

    def is_pending(self) -> bool:
        if self.ws is not None:
            return self.ws.connection_status == PENDING_CONNECTION
        return False

    def is_open(self) -> bool:
        if self.ws is not None:
            return self.ws.connection_status == CONNECTED
        return False

    async def send_message(self, request: AppRequest) -> None:

        if self.ws is None:
            raise ClientNotConnectedError("No Current Websocket Connection")

        await self.ws.send_message(request)

    async def get_response(
        self, seq: int, app_request: AppRequest, error_check: bool = True
    ) -> AppMessage:
        """
        Returns a given response from the server.
        """

        attempts = 0

        while seq in self.pending_for_response and seq not in self.responses:

            if seq in self.sent_requests:

                if attempts <= 40:

                    attempts += 1
                    await asyncio.sleep(0.1)

                else:

                    await self.send_message(app_request)
                    await asyncio.sleep(0.1)
                    attempts = 0

            if attempts <= 10:
                await asyncio.sleep(0.1)
                attempts += 1

            else:
                await self.send_message(app_request)
                await asyncio.sleep(1)
                attempts = 0

        if seq not in self.responses:
            raise ResponseNotReceivedError("Not Received")

        response = self.responses.pop(seq)

        if response.response.error.error == "rate_limit":
            logging.getLogger("rustplus.py").warning(
                "[Rustplus.py] RateLimit Exception Occurred. Retrying after bucket is full"
            )

            # Fully Refill the bucket

            self.ratelimiter.last_consumed = time.time()
            self.ratelimiter.bucket.current = 0

            while self.ratelimiter.bucket.current < self.ratelimiter.bucket.max:
                await asyncio.sleep(1)
                self.ratelimiter.bucket.refresh()

            # Reattempt the sending with a full bucket
            cost = self.ws.get_proto_cost(app_request)

            while True:

                if self.ratelimiter.can_consume(cost):
                    self.ratelimiter.consume(cost)
                    break

                await asyncio.sleep(self.ratelimiter.get_estimated_delay_time(cost))

            await self.send_message(app_request)
            response = await self.get_response(seq, app_request)

        elif self.ws.error_present(response.response.error.error) and error_check:
            raise RequestError(response.response.error.error)

        return response
