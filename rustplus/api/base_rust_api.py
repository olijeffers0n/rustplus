import asyncio
from asyncio.futures import Future
from typing import List, Callable, Union
from PIL import Image

from .structures import *
from .remote.rustplus_proto import AppEmpty, AppRequest
from .remote import RustRemote, HeartBeat, MapEventListener
from ..commands import CommandOptions, CommandHandler
from ..commands.command_data import CommandData
from ..exceptions import *
from ..utils import RegisteredListener, deprecated
from ..conversation import ConversationFactory


class BaseRustSocket:
    def __init__(
        self,
        ip: str = None,
        port: str = None,
        steam_id: int = None,
        player_token: int = None,
        command_options: CommandOptions = None,
        raise_ratelimit_exception: bool = False,
        ratelimit_limit: int = 25,
        ratelimit_refill: int = 3,
        heartbeat: HeartBeat = None,
        use_proxy: bool = False,
        use_test_server: bool = False,
    ) -> None:

        if ip is None:
            raise ValueError("Ip cannot be None")
        if steam_id is None:
            raise ValueError("SteamID cannot be None")
        if player_token is None:
            raise ValueError("PlayerToken cannot be None")

        self.ip = ip
        self.port = port
        self.steam_id = steam_id
        self.player_token = player_token
        self.seq = 1
        self.command_options = command_options
        self.raise_ratelimit_exception = raise_ratelimit_exception
        self.marker_listener = MapEventListener(self)
        self.use_test_server = use_test_server

        self.remote = RustRemote(
            ip=self.ip,
            port=self.port,
            command_options=command_options,
            ratelimit_limit=ratelimit_limit,
            ratelimit_refill=ratelimit_refill,
            use_proxy=use_proxy,
            api=self,
            loop=asyncio.get_event_loop_policy().get_event_loop(),
            use_test_server=use_test_server,
        )

        if heartbeat is None:
            raise ValueError("Heartbeat cannot be None")
        self.heartbeat = heartbeat

    async def _handle_ratelimit(self, amount=1) -> None:
        """
        Handles the ratelimit for a specific request. Will sleep if tokens are not currently available and is set to wait
        :param amount: The amount to consume
        :raises RateLimitError - If the tokens are not available and is not set to wait
        :return: None
        """
        while True:

            if self.remote.ratelimiter.can_consume(amount):
                self.remote.ratelimiter.consume(amount)
                self.heartbeat.reset_rhythm()
                return

            if self.raise_ratelimit_exception:
                raise RateLimitError("Out of tokens")

            await asyncio.sleep(
                self.remote.ratelimiter.get_estimated_delay_time(amount)
            )

    def _generate_protobuf(self) -> AppRequest:
        """
        Generates the default protobuf for a request

        :return: AppRequest - The default request object
        """
        app_request = AppRequest()
        app_request.seq = self.seq
        app_request.playerId = self.steam_id
        app_request.playerToken = self.player_token

        self.seq += 1

        return app_request

    async def connect(self, retries: int = float("inf"), delay: int = 20) -> None:
        """
        Attempts to open a connection to the rust game server specified in the constructor

        :return: None
        """
        try:
            if self.remote.ws is None:
                self.remote.connect(retries=retries, delay=delay)
                await self.heartbeat.start_beat()
        except ConnectionRefusedError:
            raise ServerNotResponsiveError("Cannot Connect")

    async def close_connection(self) -> None:
        """
        Disconnects from the Rust Server

        :return: None
        """
        self.remote.close()

    async def disconnect(self) -> None:
        """
        Disconnects from the Rust Server

        :return: None
        """
        await self.close_connection()

    async def send_wakeup_request(self) -> None:
        """
        Sends a request to the server to wake up broadcast responses

        :return: None
        """
        await self._handle_ratelimit()

        app_request = self._generate_protobuf()
        app_request.getTime.CopyFrom(AppEmpty())

        self.remote.ignored_responses.append(app_request.seq)

        await self.remote.send_message(app_request)

    async def switch_server(
        self,
        ip: str = None,
        port: str = None,
        steam_id: int = None,
        player_token: int = None,
        command_options: CommandOptions = None,
        raise_ratelimit_exception: bool = True,
        connect: bool = False,
        use_proxy: bool = False,
    ) -> None:
        """
        Disconnects and replaces server params, allowing the socket to connect to a new server.

        :param raise_ratelimit_exception: Whether to raise an exception or wait
        :param command_options: The command options
        :param ip: IP of the server
        :param port: Port of the server
        :param player_token: The player Token
        :param steam_id: Steam id of the player
        :param connect: bool indicating if socket should automatically self.connect()
        :param use_proxy: Whether to use the facepunch proxy
        :return: None
        """

        if self.use_test_server:
            raise ServerSwitchDisallowedError("Cannot switch server")

        if ip is None:
            raise ValueError("Ip cannot be None")
        if port is None:
            raise ValueError("Port cannot be None")
        if steam_id is None:
            raise ValueError("SteamID cannot be None")
        if player_token is None:
            raise ValueError("PlayerToken cannot be None")

        # disconnect before redefining
        await self.disconnect()

        # Reset basic credentials
        self.ip = ip
        self.port = port
        self.steam_id = steam_id
        self.player_token = player_token
        self.seq = 1

        # Deal with commands

        if command_options is not None:
            self.command_options = command_options
            self.remote.command_options = command_options
            if self.remote.use_commands:
                self.remote.command_handler.command_options = command_options
            else:
                self.remote.use_commands = True
                self.remote.command_handler = CommandHandler(self.command_options)

        self.raise_ratelimit_exception = raise_ratelimit_exception

        self.remote.ip = ip
        self.remote.port = port
        self.remote.use_proxy = use_proxy

        # reset ratelimiter
        self.remote.ratelimiter.reset()
        self.remote.conversation_factory = ConversationFactory(self)
        # remove entity events
        self.remote.event_handler.clear_entity_events()
        # reset marker listener
        self.marker_listener.persistent_ids.clear()
        self.marker_listener.highest_id = 0

        if connect:
            await self.connect()

    def command(
        self,
        coro: Callable = None,
        aliases: List[str] = None,
        alias_func: Callable = None,
    ) -> Union[Callable, RegisteredListener]:
        """
        A coroutine decorator used to register a command executor

        :param alias_func: The function to test the aliases against
        :param aliases: The aliases to register the command under
        :param coro: The coroutine to call when the command is called
        :return: RegisteredListener - The listener object | Callable - The callable func for the decorator
        """

        if isinstance(coro, RegisteredListener):
            coro = coro.get_coro()

        if asyncio.iscoroutinefunction(coro):
            cmd_data = CommandData(coro, asyncio.get_event_loop(), aliases, alias_func)
            self.remote.command_handler.register_command(cmd_data)
            return RegisteredListener(coro.__name__, (cmd_data.coro, cmd_data.loop))

        def wrap_func(coro):

            if self.command_options is None:
                raise CommandsNotEnabledError("Not enabled")

            if isinstance(coro, RegisteredListener):
                coro = coro.get_coro()

            cmd_data = CommandData(coro, asyncio.get_event_loop(), aliases, alias_func)
            self.remote.command_handler.register_command(cmd_data)
            return RegisteredListener(coro.__name__, (cmd_data.coro, cmd_data.loop))

        return wrap_func

    def team_event(self, coro) -> RegisteredListener:
        """
        A Decorator to register an event listener for team changes

        :param coro: The coroutine to call when a change happens
        :return: RegisteredListener - The listener object
        """

        if isinstance(coro, RegisteredListener):
            coro = coro.get_coro()

        data = (coro, asyncio.get_event_loop())
        listener = RegisteredListener("team_changed", data)
        self.remote.event_handler.register_event(listener)
        return listener

    def chat_event(self, coro) -> RegisteredListener:
        """
        A Decorator to register an event listener for chat messages

        :param coro: The coroutine to call when a message is sent
        :return: RegisteredListener - The listener object
        """

        if isinstance(coro, RegisteredListener):
            coro = coro.get_coro()

        data = (coro, asyncio.get_event_loop())
        listener = RegisteredListener("chat_message", data)

        self.remote.event_handler.register_event(listener)

        return listener

    def entity_event(self, eid):
        """
        Decorator to register a smart device listener

        :param eid: The entity id of the entity
        :return: RegisteredListener - The listener object
        :raises SmartDeviceRegistrationError
        """

        if not self.remote.is_open():
            raise ClientNotConnectedError("Client is not connected")

        def wrap_func(coro) -> RegisteredListener:

            if isinstance(coro, RegisteredListener):
                coro = coro.get_coro()

            async def get_entity(self, eid) -> RustEntityInfo:

                await self._handle_ratelimit()

                app_request = self._generate_protobuf()
                app_request.entityId = eid
                app_request.getEntityInfo.CopyFrom(AppEmpty())

                await self.remote.send_message(app_request)

                return await self.remote.get_response(
                    app_request.seq, app_request, False
                )

            def entity_event_callback(future_inner: Future):

                entity_info = future_inner.result()

                if entity_info.response.HasField("error"):
                    raise SmartDeviceRegistrationError("Not Found")

                self.remote.event_handler.register_event(
                    RegisteredListener(
                        eid, (coro, loop, entity_info.response.entityInfo.type)
                    )
                )

            loop = asyncio.get_event_loop()
            future = asyncio.run_coroutine_threadsafe(get_entity(self, eid), loop)
            future.add_done_callback(entity_event_callback)

            return RegisteredListener(eid, (coro))

        return wrap_func

    async def start_marker_event_listener(self, delay: int = 5) -> None:
        """
        Starts the marker event listener
        :param delay: The delay between marker checking
        :return: None
        """
        self.marker_listener.start(delay)

    def marker_event(self, coro) -> RegisteredListener:
        """
        A Decorator to register an event listener for new map markers

        :param coro: The coroutine to call when the command is called
        :return: RegisteredListener - The listener object
        """

        if isinstance(coro, RegisteredListener):
            coro = coro.get_coro()

        if not self.marker_listener:
            raise ValueError("Marker listener not started")

        data = (coro, asyncio.get_event_loop())
        listener = RegisteredListener("map_marker", data)
        self.marker_listener.add_listener(listener)
        return listener

    def protobuf_received(self, coro) -> RegisteredListener:
        """
        A Decorator to register an event listener for protobuf being received on the websocket

        :param coro: The coroutine to call when the command is called
        :return: RegisteredListener - The listener object
        """

        if isinstance(coro, RegisteredListener):
            coro = coro.get_coro()

        data = (coro, asyncio.get_event_loop())
        listener = RegisteredListener("protobuf_received", data)
        self.remote.event_handler.register_event(listener)
        return listener

    def remove_listener(self, listener) -> bool:
        """
        This will remove a listener, command or event. Takes a RegisteredListener instance

        :return: Success of removal. True = Removed. False = Not Removed
        """

        if isinstance(listener, RegisteredListener):
            if listener.listener_id == "map_marker":
                return self.marker_listener.remove_listener(listener)
            return self.remote.remove_listener(listener)
        return False

    @staticmethod
    async def hang() -> None:
        """
        This Will permanently put your script into a state of 'hanging' Cannot be Undone. Only do this in scripts
        using commands

        :returns Nothing, This will never return
        """

        while True:
            await asyncio.sleep(1)

    def get_conversation_factory(self) -> ConversationFactory:
        """
        Gets the current ConversationFactory object

        :returns ConversationFactory: the factory
        """
        return self.remote.conversation_factory

    async def get_time(self) -> RustTime:
        """
        Gets the current in-game time from the server.

        :returns RustTime: The Time
        """
        raise NotImplementedError("Not Implemented")

    async def send_team_message(self, message: str) -> None:
        """
        Sends a message to the in-game team chat

        :param message: The string message to send
        """
        raise NotImplementedError("Not Implemented")

    async def get_info(self) -> RustInfo:
        """
        Gets information on the Rust Server
        :return: RustInfo - The info of the server
        """
        raise NotImplementedError("Not Implemented")

    async def get_team_chat(self) -> List[RustChatMessage]:
        """
        Gets the team chat from the server

        :return List[RustChatMessage]: The chat messages in the team chat
        """
        raise NotImplementedError("Not Implemented")

    async def get_team_info(self) -> RustTeamInfo:
        """
        Gets Information on the members of your team

        :return RustTeamInfo: The info of your team
        """
        raise NotImplementedError("Not Implemented")

    async def get_markers(self) -> List[RustMarker]:
        """
        Gets all the map markers from the server

        :return List[RustMarker]: All the markers on the map
        """
        raise NotImplementedError("Not Implemented")

    async def get_map(
        self,
        add_icons: bool = False,
        add_events: bool = False,
        add_vending_machines: bool = False,
        override_images: dict = None,
        add_grid: bool = False,
    ) -> Image:
        """
        Gets an image of the map from the server with the specified additions

        :param add_icons: To add the monument icons
        :param add_events: To add the Event icons
        :param add_vending_machines: To add the vending icons
        :param override_images: To override the images pre-supplied with RustPlus.py
        :param add_grid: To add the grid to the map
        :return Image: PIL Image
        """
        raise NotImplementedError("Not Implemented")

    async def get_raw_map_data(self) -> RustMap:
        """
        Gets the raw map data from the server

        :return RustMap: The raw map of the server
        """
        raise NotImplementedError("Not Implemented")

    async def get_entity_info(self, eid: int = None) -> RustEntityInfo:
        """
        Gets entity info from the server

        :param eid: The Entities ID
        :return RustEntityInfo: The entity Info
        """
        raise NotImplementedError("Not Implemented")

    async def turn_on_smart_switch(self, eid: int = None) -> None:
        """
        Turns on a given smart switch by entity ID

        :param eid: The Entities ID
        :return None:
        """
        raise NotImplementedError("Not Implemented")

    async def turn_off_smart_switch(self, eid: int = None) -> None:
        """
        Turns off a given smart switch by entity ID

        :param eid: The Entities ID
        :return None:
        """
        raise NotImplementedError("Not Implemented")

    async def promote_to_team_leader(self, steamid: int = None) -> None:
        """
        Promotes a given user to the team leader by their 64-bit Steam ID

        :param steamid: The SteamID of the player to promote
        :return None:
        """
        raise NotImplementedError("Not Implemented")

    @deprecated("Use RustSocket#get_markers")
    async def get_current_events(self) -> List[RustMarker]:
        """
        Returns all the map markers that are for events:
        Can detect:
            - Explosion
            - CH47 (Chinook)
            - Cargo Ship
            - Locked Crate
            - Attack Helicopter

        :return List[RustMarker]: All current events
        """
        raise NotImplementedError("Not Implemented")

    async def get_contents(
        self, eid: int = None, combine_stacks: bool = False
    ) -> RustContents:
        """
        Gets the contents of a storage monitor-attached container

        :param eid: The EntityID Of the storage Monitor
        :param combine_stacks: Whether to combine alike stacks together
        :return RustContents: The contents on the monitor
        """
        raise NotImplementedError("Not Implemented")

    @deprecated("Use RustSocket#get_contents")
    async def get_tc_storage_contents(
        self, eid: int = None, combine_stacks: bool = False
    ) -> RustContents:
        """
        Gets the Information about TC Upkeep and Contents.
        Do not use this for any other storage monitor than a TC
        """
        raise NotImplementedError("Not Implemented")
