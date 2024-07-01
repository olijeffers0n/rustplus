import asyncio
from collections import defaultdict
from datetime import datetime
from typing import List, Union
import logging
from PIL import Image

from .commands import CommandOptions
from .identification import ServerDetails
from .remote.camera import CameraManager
from .remote.rustplus_proto import (
    AppRequest,
    AppEmpty,
    AppSendMessage,
    AppSetEntityValue,
    AppPromoteToLeader,
    AppCameraSubscribe,
)
from .remote.websocket import RustWebsocket
from .structs import (
    RustTime,
    RustInfo,
    RustChatMessage,
    RustTeamInfo,
    RustMarker,
    RustMap,
    RustEntityInfo,
    RustContents,
    RustItem,
)
from .utils import convert_time, translate_id_to_stack
from .remote.ratelimiter import RateLimiter


class RustSocket:

    def __init__(
        self,
        server_details: ServerDetails,
        ratelimiter: Union[None, RateLimiter] = None,
        command_options: Union[None, CommandOptions] = None,
    ) -> None:
        self.server_details = server_details
        self.command_options = command_options
        self.logger = logging.getLogger("rustplus.py")

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.DEBUG)

        self.ws = RustWebsocket(self.server_details, self.command_options)
        self.seq = 1

        if ratelimiter:
            self.ratelimiter = ratelimiter
        else:
            self.ratelimiter = RateLimiter()

        self.ratelimiter.add_socket(
            self.server_details,
            RateLimiter.SERVER_LIMIT,
            RateLimiter.SERVER_LIMIT,
            1,
            RateLimiter.SERVER_REFRESH_AMOUNT,
        )

    async def _handle_ratelimit(self, tokens) -> None:
        while True:
            if await self.ratelimiter.can_consume(self.server_details, tokens):
                await self.ratelimiter.consume(self.server_details, tokens)
                break

            await asyncio.sleep(
                await self.ratelimiter.get_estimated_delay_time(
                    self.server_details, tokens
                )
            )

    async def _generate_request(self, tokens=1) -> AppRequest:
        await self._handle_ratelimit(tokens)

        app_request = AppRequest()
        app_request.seq = self.seq
        self.seq += 1
        app_request.player_id = self.server_details.player_id
        app_request.player_token = self.server_details.player_token

        return app_request

    async def connect(self) -> None:
        await self.ws.connect()
        await self.get_time()  # Wake up the connection

    @staticmethod
    async def hang() -> None:
        """
        This Will permanently put your script into a state of 'hanging' Cannot be Undone. Only do this in scripts
        using commands

        :returns Nothing, This will never return
        """

        while True:
            await asyncio.sleep(1)

    async def get_time(self) -> Union[RustTime, None]:
        """
        Gets the current in-game time from the server.

        :returns RustTime: The Time
        """

        packet = await self._generate_request()
        packet.get_time = AppEmpty()
        packet = await self.ws.send_and_get(packet)

        if packet is None:
            return None

        return RustTime(
            packet.response.time.day_length_minutes,
            convert_time(packet.response.time.sunrise),
            convert_time(packet.response.time.sunset),
            convert_time(packet.response.time.time),
            packet.response.time.time,
            packet.response.time.time_scale,
        )

    async def send_team_message(self, message: str) -> None:
        """
        Sends a message to the in-game team chat

        :param message: The string message to send
        """

        packet = await self._generate_request(tokens=2)
        send_message = AppSendMessage()
        send_message.message = message
        packet.send_team_message = send_message

        await self.ws.send_message(packet, True)

    async def get_info(self) -> Union[RustInfo, None]:
        """
        Gets information on the Rust Server
        :return: RustInfo - The info of the server
        """
        packet = await self._generate_request()
        packet.get_info = AppEmpty()

        response = await self.ws.send_and_get(packet)
        if response is None:
            return None

        return RustInfo(response.response.info)

    async def get_team_chat(self) -> Union[List[RustChatMessage], None]:
        """
        Gets the team chat from the server

        :return List[RustChatMessage]: The chat messages in the team chat
        """
        packet = await self._generate_request()
        packet.get_team_chat = AppEmpty()

        response = await self.ws.send_and_get(packet)
        if response is None:
            return None

        return [
            RustChatMessage(message)
            for message in (response).response.team_chat.messages
        ]

    async def get_team_info(self) -> Union[RustTeamInfo, None]:
        """
        Gets Information on the members of your team

        :return RustTeamInfo: The info of your team
        """
        packet = await self._generate_request()
        packet.get_team_info = AppEmpty()

        response = await self.ws.send_and_get(packet)
        if response is None:
            return None

        return RustTeamInfo(response.response.team_info)

    async def get_markers(self) -> Union[List[RustMarker], None]:
        """
        Gets all the map markers from the server

        :return List[RustMarker]: All the markers on the map
        """
        packet = await self._generate_request()
        packet.get_map_markers = AppEmpty()

        response = await self.ws.send_and_get(packet)
        if response is None:
            return None

        return [
            RustMarker(marker) for marker in (response).response.map_markers.markers
        ]

    async def get_map(
        self,
        add_icons: bool = False,
        add_events: bool = False,
        add_vending_machines: bool = False,
        override_images: dict = None,
        add_grid: bool = False,
    ) -> Image.Image:
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

    async def get_map_info(self) -> Union[RustMap, None]:
        """
        Gets the raw map data from the server

        :return RustMap: The raw map of the server
        """
        packet = await self._generate_request(tokens=5)
        packet.get_map = AppEmpty()

        response = await self.ws.send_and_get(packet)
        if response is None:
            return None

        return RustMap(response.response.map)

    async def get_entity_info(self, eid: int = None) -> Union[RustEntityInfo, None]:
        """
        Gets entity info from the server

        :param eid: The Entities ID
        :return RustEntityInfo: The entity Info
        """
        packet = await self._generate_request()
        packet.get_entity_info = AppEmpty()
        packet.entity_id = eid

        response = await self.ws.send_and_get(packet)
        if response is None:
            return None

        return RustEntityInfo(response.response.entity_info)

    async def set_entity_value(self, eid: int = None, value: bool = False) -> None:
        """
        Turns off a given smart switch by entity ID

        :param eid: The Entities ID
        :param value: The value to set
        :return None:
        """
        packet = await self._generate_request()
        value = AppSetEntityValue()
        value.value = value
        packet.set_entity_value = AppEmpty()
        packet.entity_id = eid

        await self.ws.send_message(packet, True)

    async def promote_to_team_leader(self, steamid: int = None) -> None:
        """
        Promotes a given user to the team leader by their 64-bit Steam ID

        :param steamid: The SteamID of the player to promote
        :return None:
        """
        packet = await self._generate_request()
        promote_packet = AppPromoteToLeader()
        promote_packet.steam_id = steamid
        packet.promote_to_leader = promote_packet

        await self.ws.send_message(packet, True)

    async def get_contents(
        self, eid: int = None, combine_stacks: bool = False
    ) -> Union[RustContents, None]:
        """
        Gets the contents of a storage monitor-attached container

        :param eid: The EntityID Of the storage Monitor
        :param combine_stacks: Whether to combine alike stacks together
        :return RustContents: The contents on the monitor
        """
        returned_data = await self.get_entity_info(eid)

        if returned_data is None:
            return None

        target_time = datetime.utcfromtimestamp(int(returned_data.protection_expiry))
        difference = target_time - datetime.utcnow()

        items = []

        for item in returned_data.items:
            items.append(
                RustItem(
                    translate_id_to_stack(item.item_id),
                    item.item_id,
                    item.quantity,
                    item.item_is_blueprint,
                )
            )

        if combine_stacks:
            merged_map = defaultdict(tuple)

            for item in items:
                data = merged_map[str(item.item_id)]
                if data:
                    count = int(data[0]) + int(item.quantity)
                    merged_map[str(item.item_id)] = (count, bool(item.is_blueprint))
                else:
                    merged_map[str(item.item_id)] = (
                        int(item.quantity),
                        bool(item.is_blueprint),
                    )

            items = []
            for key in merged_map.keys():
                items.append(
                    RustItem(
                        translate_id_to_stack(key),
                        key,
                        int(merged_map[key][0]),
                        bool(merged_map[key][1]),
                    )
                )

        return RustContents(difference, bool(returned_data.has_protection), items)

    async def get_camera_manager(self, cam_id: str) -> Union[CameraManager, None]:
        """
        Gets a camera manager for a given camera ID

        NOTE: This will override the current camera manager if one exists for the given ID so you cannot have multiple

        :param cam_id: The ID of the camera
        :return CameraManager: The camera manager
        :raises RequestError: If the camera is not found, or you cannot access it. See reason for more info
        """
        packet = await self._generate_request()
        subscribe = AppCameraSubscribe()
        subscribe.camera_id = cam_id
        packet.camera_subscribe = subscribe

        response = await self.ws.send_and_get(packet)

        if response is None:
            return None

        return CameraManager(self, cam_id, response.response.camera_subscribe_info)
