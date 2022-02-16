import asyncio
from asyncio.futures import Future
from typing import List
from PIL import Image

from .structures import *
from .remote.rustplus_pb2 import *
from .remote import RustRemote, HeartBeat
from ..commands import CommandOptions
from ..exceptions import *
from ..utils import RegisteredListener


class BaseRustSocket:

    def __init__(self, ip: str = None, port: str = None, steamid: int = None, playertoken: int = None,
                 command_options: CommandOptions = None, raise_ratelimit_exception: bool = True,
                 ratelimit_limit: int = 25, ratelimit_refill: int = 3, heartbeat: HeartBeat = None) -> None:

        if ip is None:
            raise ValueError("Ip cannot be None")
        if port is None:
            raise ValueError("Port cannot be None")
        if steamid is None:
            raise ValueError("SteamID cannot be None")
        if playertoken is None:
            raise ValueError("PlayerToken cannot be None")

        self.ip = ip
        self.port = port
        self.steamid = steamid
        self.player_token = playertoken
        self.seq = 1
        self.command_options = command_options
        self.raise_ratelimit_exception = raise_ratelimit_exception
        self.listener_seq = 0

        self.remote = RustRemote(ip=self.ip, port=self.port, command_options=command_options,
                                 ratelimit_limit=ratelimit_limit, ratelimit_refill=ratelimit_refill)

        if heartbeat is None:
            raise ValueError("Heartbeat cannot be None")
        self.heartbeat = heartbeat

    async def _handle_ratelimit(self, amount=1) -> None:
        """
        Handles the ratelimit for a specific request
        """

        while True:

            if self.remote.ratelimiter.can_consume(amount):
                self.remote.ratelimiter.consume(amount)
                self.heartbeat.reset_rhythm()
                return

            if self.raise_ratelimit_exception:
                raise RateLimitError("Out of tokens")

            await asyncio.sleep(self.remote.ratelimiter.get_estimated_delay_time(amount))

    def _generate_protobuf(self) -> AppRequest:
        """
        Generates the empty AppRequest Message
        """

        app_request = AppRequest()
        app_request.seq = self.seq
        app_request.playerId = self.steamid
        app_request.playerToken = self.player_token

        self.seq += 1

        return app_request

    async def connect(self) -> None:
        """
        Opens the connection to the Rust Server
        """
        try:
            if self.remote.ws is None:
                self.remote.connect()
                await self.send_wakeup_request()
                await self.heartbeat.start_beat()
        except ConnectionRefusedError:
            raise ServerNotResponsiveError("Cannot Connect")

    async def close_connection(self) -> None:
        """
        Disconnects from the Rust Server
        """
        self.remote.close()

    async def disconnect(self) -> None:
        """
        Disconnects from the Rust Server
        """
        await self.close_connection()

    async def send_wakeup_request(self) -> None:
        """
        Sends a request to the server to wake up broadcast responses
        """
        await self._handle_ratelimit()

        app_request = self._generate_protobuf()
        app_request.getTime.CopyFrom(AppEmpty())

        self.remote.ignored_responses.append(app_request.seq)

        await self.remote.send_message(app_request)

    def command(self, coro) -> RegisteredListener:
        """
        A Decorator to register a command listener
        """

        if self.command_options is None:
            raise CommandsNotEnabledError("Not enabled")

        if isinstance(coro, RegisteredListener):
            coro = coro.get_coro()

        data = (coro, asyncio.get_event_loop())
        self.remote.command_handler.register_command(coro.__name__, data)
        return RegisteredListener(coro.__name__, data)

    def team_event(self, coro) -> RegisteredListener:
        """
        A Decorator to register an event listener for team changes
        """

        if isinstance(coro, RegisteredListener):
            coro = coro.get_coro()

        data = (coro, asyncio.get_event_loop())
        self.remote.event_handler.register_event("team_changed", data)
        return RegisteredListener("team_changed", data)

    def chat_event(self, coro) -> RegisteredListener:
        """
        A Decorator to register an event listener for chat messages
        """

        if isinstance(coro, RegisteredListener):
            coro = coro.get_coro()

        data = (coro, asyncio.get_event_loop())
        self.remote.event_handler.register_event("chat_message", data)
        return RegisteredListener("chat_message", data)

    def entity_event(self, eid):
        """
        Decorator to register a smart device listener
        """

        def wrap_func(coro) -> RegisteredListener:

            if isinstance(coro, RegisteredListener):
                coro = coro.get_coro()

            def entity_event_callback(future_inner: Future):
                try:
                    entity_info: RustEntityInfo = future_inner.result()
                    self.remote.event_handler.register_event(eid, (coro, loop, entity_info.type))
                except Exception:
                    raise SmartDeviceRegistrationError("Not Found")

            loop = asyncio.get_event_loop()
            future = asyncio.run_coroutine_threadsafe(self.get_entity_info(eid), loop)
            future.add_done_callback(entity_event_callback)

            return RegisteredListener(eid, coro)

        return wrap_func

    def remove_listener(self, listener) -> bool:
        """
        This will remove a listener, command or event. Takes a RegisteredListener instance
        :returns Success of removal. True = Removed. False = Not Removed
        """

        if isinstance(listener, RegisteredListener):
            return self.remote.remove_listener(listener)
        return False

    @staticmethod
    async def hang() -> None:
        """
        This Will permanently put your script into a state of 'hanging' Cannot be Undone. Only do this in scripts using commands
        """

        while True:
            await asyncio.sleep(1)

    async def get_time(self) -> RustTime:
        """
        Gets the current in-game time from the server. Returns a RustTime object
        """
        raise NotImplementedError("Not Implemented")

    async def send_team_message(self, message: str) -> None:
        """
        Sends a message to the in-game team chat
        """
        raise NotImplementedError("Not Implemented")

    async def get_info(self) -> RustInfo:
        """
        Gets information on the Rust Server
        """
        raise NotImplementedError("Not Implemented")

    async def get_team_chat(self) -> List[RustChatMessage]:
        """
        Gets the team chat from the server
        """
        raise NotImplementedError("Not Implemented")

    async def get_team_info(self):
        """
        Gets Information on the members of your team
        """
        raise NotImplementedError("Not Implemented")

    async def get_markers(self) -> List[RustMarker]:
        """
        Gets all the map markers from the server
        """
        raise NotImplementedError("Not Implemented")

    async def get_map(self, add_icons: bool = False, add_events: bool = False, add_vending_machines: bool = False,
                      override_images: dict = None) -> Image:
        """
        Gets an image of the map from the server with the specified additions
        """
        raise NotImplementedError("Not Implemented")

    async def get_raw_map_data(self) -> RustMap:
        """
        Gets the raw map data from the server
        """
        raise NotImplementedError("Not Implemented")

    async def get_entity_info(self, eid: int = None) -> RustEntityInfo:
        """
        Gets entity info from the server
        """
        raise NotImplementedError("Not Implemented")

    async def turn_on_smart_switch(self, eid: int = None) -> None:
        """
        Turns on a given smart switch by entity ID
        """
        raise NotImplementedError("Not Implemented")

    async def turn_off_smart_switch(self, eid: int = None) -> None:
        """
        Turns off a given smart switch by entity ID
        """
        raise NotImplementedError("Not Implemented")

    async def promote_to_team_leader(self, steamid: int = None) -> None:
        """
        Promotes a given user to the team leader by their 64-bit Steam ID
        """
        raise NotImplementedError("Not Implemented")

    async def get_current_events(self) -> List[RustMarker]:
        """
        Returns all the map markers that are for events:
        Can detect:
            - Explosion
            - CH47 (Chinook)
            - Cargo Ship
            - Locked Crate
            - Attack Helicopter
        """
        raise NotImplementedError("Not Implemented")

    async def get_tc_storage_contents(self, eid: int = None, combine_stacks: bool = False) -> RustContents:
        """
        Gets the Information about TC Upkeep and Contents.
        Do not use this for any other storage monitor than a TC
        """
        raise NotImplementedError("Not Implemented")
