import asyncio
from typing import List
from PIL import Image

from .structures import *
from .remote.rustplus_pb2 import *
from .remote import RustRemote, HeartBeat
from ..commands import CommandOptions
from ..exceptions import *

class BaseRustSocket:

    def __init__(self, ip : str = None, port : str = None, steamid : int = None, playertoken : int = None, command_options : CommandOptions = None, raise_ratelimit_exception : bool = True, ratelimit_limit : int = 25, ratelimit_refill : int = 3, heartbeat : HeartBeat = None) -> None:
        
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
        self.playertoken = playertoken
        self.seq = 1
        self.command_options = command_options
        self.raise_ratelimit_exception = raise_ratelimit_exception

        self.remote = RustRemote(ip=self.ip, port=self.port, command_options=command_options, ratelimit_limit=ratelimit_limit, ratelimit_refill=ratelimit_refill)
        
        if heartbeat is None:
            raise ValueError("Heartbeat cannot be None")
        self.heartbeat = heartbeat

    async def _handle_ratelimit(self, amount = 1) -> None:
        """
        Handles the ratelimit for a specific request
        """

        while True:

            if self.remote.ratelimiter.can_consume(amount):
                self.remote.ratelimiter.consume(amount)
                self.heartbeat.reset_rythm()
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
        app_request.playerToken = self.playertoken

        self.seq += 1

        return app_request

    async def connect(self) -> None:
        """
        Opens the connection to the Rust Server
        """
        try:
            if self.remote.ws is None:
                self.remote.connect()
                await self._send_wakeup_request()
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

    async def _send_wakeup_request(self) -> None:
        """
        Sends a request to the server to wake up broadcast responses
        """
        await self._handle_ratelimit()

        app_request = self._generate_protobuf()
        app_request.getTime.CopyFrom(AppEmpty())

        self.remote.ignored_responses.append(app_request.seq)

        await self.remote.send_message(app_request)
    
    def command(self, coro) -> None:
        """
        A Decorator to register a command listener
        """

        if self.command_options is None:
            raise CommandsNotEnabledError("Not enabled")

        self.remote.command_handler.registerCommand(coro.__name__, coro, asyncio.get_event_loop())

    def team_event(self, coro) -> None:
        """
        A Decorator to register an event listener for team changes
        """

        self.remote.event_handler.register_event("team_changed", (coro, asyncio.get_event_loop()))

    def chat_event(self, coro) -> None:
        """
        A Decorator to register an event listener for chat messages
        """

        self.remote.event_handler.register_event("chat_message", (coro, asyncio.get_event_loop()))

    async def hang(self) -> None:
        """This Will permanently put your script into a state of 'hanging' Cannot be Undone. Only do this in scripts using commands"""

        while True:
            await asyncio.sleep(1)

    async def get_time(self) -> RustTime:
        """
        Gets the current in-game time from the server. Returns a RustTime object
        """
        pass

    async def send_team_message(self, message : str) -> None:
        """
        Sends a message to the in-game team chat
        """
        pass

    async def get_info(self) -> RustInfo:
        """
        Gets information on the Rust Server
        """
        pass

    async def get_team_chat(self) -> List[RustChatMessage]:
        """
        Gets the team chat from the server
        """
        pass

    async def get_team_info(self):
        """
        Gets Information on the members of your team
        """
        pass

    async def get_markers(self) -> List[RustMarker]:
        """
        Gets all the map markers from the server
        """
        pass

    async def get_map(self, add_icons : bool = False, add_events : bool = False, add_vending_machines : bool = False, override_images : dict = {}) -> Image:
        """
        Gets an image of the map from the server with the specified additions
        """
        pass

    async def get_raw_map_data(self) -> RustMap:
        """
        Gets the raw map data from the server
        """
        pass

    async def get_entity_info(self, eid : int = None) -> RustEntityInfo:
        """
        Gets entity info from the server
        """
        pass

    async def turn_on_smart_switch(self, eid : int = None) -> None:
        """
        Turns on a given smart switch by entity ID
        """
        pass

    async def turn_off_smart_switch(self, eid : int = None) -> None:
        """
        Turns off a given smart switch by entity ID
        """
        pass

    async def promote_to_team_leader(self, steamid : int = None) -> None:
        """
        Promotes a given user to the team leader by their 64-bit Steam ID
        """
        pass

    async def get_current_events(self) -> List[RustMarker]:
        """
        Returns all the map markers that are for events:
        Can detect:
            - Explosion
            - CH47 (Chinook)
            - Cargo Ship
            - Locked Crate
        """
        pass

    async def get_tc_storage_contents(self, eid : int = None, combine_stacks : bool = False) -> RustContents:
        """
        Gets the Information about TC Upkeep and Contents.
        Do not use this for any other storage monitor than a TC
        """
        pass
