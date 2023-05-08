import asyncio
import logging
from asyncio import Future
from typing import Union, Dict

from .camera.camera_manager import CameraManager
from .events import EventLoopManager, EntityEvent, RegisteredListener
from .rustplus_proto import AppRequest, AppMessage, AppEmpty, AppCameraSubscribe
from .rustws import RustWebsocket, CONNECTED, PENDING_CONNECTION
from .ratelimiter import RateLimiter
from .expo_bundle_handler import MagicValueGrabber
from ...utils import ServerID, YieldingEvent
from ...conversation import ConversationFactory
from ...commands import CommandHandler
from ...exceptions import (
    ClientNotConnectedError,
    RequestError,
    SmartDeviceRegistrationError,
)


class RustRemote:
    def __init__(
        self,
        server_id: ServerID,
        command_options,
        ratelimit_limit,
        ratelimit_refill,
        use_proxy: bool = False,
        api=None,
        use_test_server: bool = False,
        rate_limiter: RateLimiter = None,
    ) -> None:
        self.server_id = server_id
        self.api = api
        self.command_options = command_options
        self.ratelimit_limit = ratelimit_limit
        self.ratelimit_refill = ratelimit_refill
        self.use_proxy = use_proxy
        if isinstance(rate_limiter, RateLimiter):
            self.ratelimiter = rate_limiter
        else:
            self.ratelimiter = RateLimiter.default()

        self.ratelimiter.add_socket(
            self.server_id, ratelimit_limit, ratelimit_limit, 1, ratelimit_refill
        )
        self.ws = None
        self.logger = logging.getLogger("rustplus.py")

        self.ignored_responses = set()
        self.pending_response_events: Dict[int, YieldingEvent] = {}

        self.command_handler = None
        if command_options is None:
            self.use_commands = False
        else:
            self.use_commands = True
            self.command_handler = CommandHandler(self.command_options, api)

        self.magic_value = MagicValueGrabber.get_magic_value()
        self.conversation_factory = ConversationFactory(api)
        self.use_test_server = use_test_server
        self.pending_entity_subscriptions = []
        self.camera_manager: Union[CameraManager, None] = None

    async def connect(self, retries, delay, on_failure=None) -> None:
        self.ws = RustWebsocket(
            server_id=self.server_id,
            remote=self,
            use_proxy=self.use_proxy,
            magic_value=self.magic_value,
            use_test_server=self.use_test_server,
            on_failure=on_failure,
            delay=delay,
        )
        await self.ws.connect(retries=retries)

        for entity_id, coroutine in self.pending_entity_subscriptions:
            self.handle_subscribing_entity(entity_id, coroutine)

    async def close(self) -> None:
        if self.ws is not None:
            await self.ws.close()
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

        self.pending_response_events[request.seq] = YieldingEvent()
        await self.ws.send_message(request)

    async def get_response(
        self, seq: int, app_request: AppRequest, error_check: bool = True
    ) -> AppMessage:
        """
        Returns a given response from the server.
        """

        attempts = 1

        while True:
            event = self.pending_response_events.get(seq)
            if event is None:
                raise Exception("Event Doesn't exist")

            response: AppMessage = await event.event_wait_for(4)
            if response is not None:
                break

            await self.send_message(app_request)

            if attempts % 150 == 0:
                self.logger.info(
                    f"[RustPlus.py] Been waiting 10 minutes for a response for seq {seq}"
                )

            attempts += 1

        self.pending_response_events.pop(seq)

        if response.response.error.error == "rate_limit":
            logging.getLogger("rustplus.py").warning(
                "[Rustplus.py] RateLimit Exception Occurred. Retrying after bucket is full"
            )

            # Fully Refill the bucket
            bucket = self.ratelimiter.socket_buckets.get(self.server_id)
            bucket.current = 0

            while bucket.current < bucket.max:
                await asyncio.sleep(1)
                bucket.refresh()

            # Reattempt the sending with a full bucket
            cost = self.ws.get_proto_cost(app_request)

            while True:
                if await self.ratelimiter.can_consume(self.server_id, cost):
                    await self.ratelimiter.consume(self.server_id, cost)
                    break

                await asyncio.sleep(
                    await self.ratelimiter.get_estimated_delay_time(self.server_id, cost)
                )

            await self.send_message(app_request)
            response = await self.get_response(seq, app_request)

        elif self.ws.error_present(response.response.error.error) and error_check:
            raise RequestError(response.response.error.error)

        return response

    def handle_subscribing_entity(self, entity_id: int, coroutine) -> None:
        if not self.is_open():
            self.pending_entity_subscriptions.append((entity_id, coroutine))
            return

        async def get_entity_info(remote: RustRemote, eid):
            await remote.api._handle_ratelimit()

            app_request: AppRequest = remote.api._generate_protobuf()
            app_request.entityId = eid
            app_request.get_entity_info = AppEmpty()
            app_request.get_entity_info._serialized_on_wire = True

            await remote.send_message(app_request)

            return await remote.get_response(app_request.seq, app_request, False)

        def entity_event_callback(future_inner: Future) -> None:
            entity_info = future_inner.result()

            if entity_info.response.HasField("error"):
                raise SmartDeviceRegistrationError(
                    f"Entity: '{entity_id}' has not been found"
                )

            EntityEvent.handlers.register(
                RegisteredListener(
                    entity_id, (coroutine, entity_info.response.entityInfo.type)
                ),
                self.server_id,
            )

        future = asyncio.run_coroutine_threadsafe(
            get_entity_info(self, entity_id), EventLoopManager.get_loop(self.server_id)
        )
        future.add_done_callback(entity_event_callback)

    async def subscribe_to_camera(
        self, entity_id: int, ignore_response: bool = False
    ) -> AppRequest:
        await self.api._handle_ratelimit()
        app_request: AppRequest = self.api._generate_protobuf()
        subscribe = AppCameraSubscribe()
        subscribe.camera_id = entity_id
        app_request.camera_subscribe = subscribe

        await self.send_message(app_request)

        if ignore_response:
            await self.add_ignored_response(app_request.seq)

        return app_request

    async def create_camera_manager(self, cam_id) -> CameraManager:
        if self.camera_manager is not None:
            if self.camera_manager._cam_id == cam_id:
                return self.camera_manager

        app_request = await self.subscribe_to_camera(cam_id)
        app_message = await self.get_response(app_request.seq, app_request)

        self.camera_manager = CameraManager(
            self.api, cam_id, app_message.response.camera_subscribe_info
        )
        return self.camera_manager

    async def add_ignored_response(self, seq) -> None:
        self.ignored_responses.add(seq)
