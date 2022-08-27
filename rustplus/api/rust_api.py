import requests
from typing import List
from PIL import Image
from io import BytesIO
from datetime import datetime
from collections import defaultdict
from importlib import resources

from .base_rust_api import BaseRustSocket
from .structures import (
    RustInfo,
    RustMap,
    RustMarker,
    RustChatMessage,
    RustTeamInfo,
    RustEntityInfo,
    RustContents,
    RustItem,
)
from .remote.rustplus_proto import *
from .remote import HeartBeat
from ..commands import CommandOptions
from ..exceptions import *
from ..utils import (
    RustTime,
    format_time,
    format_coord,
    convert_marker,
    convert_monument,
    translate_id_to_stack,
    deprecated,
)


class RustSocket(BaseRustSocket):
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
        use_proxy: bool = False,
        use_test_server: bool = False,
    ) -> None:
        super().__init__(
            ip=ip,
            port=port,
            steam_id=steam_id,
            player_token=player_token,
            command_options=command_options,
            raise_ratelimit_exception=raise_ratelimit_exception,
            ratelimit_limit=ratelimit_limit,
            ratelimit_refill=ratelimit_refill,
            heartbeat=HeartBeat(self),
            use_proxy=use_proxy,
            use_test_server=use_test_server,
        )

    async def get_time(self) -> RustTime:

        await self._handle_ratelimit()

        app_request = self._generate_protobuf()
        app_request.getTime.CopyFrom(AppEmpty())

        await self.remote.send_message(app_request)

        response = await self.remote.get_response(app_request.seq, app_request)

        return format_time(response)

    async def send_team_message(self, message: str) -> None:

        await self._handle_ratelimit(2)

        app_send_message = AppSendMessage()
        app_send_message.message = message

        app_request = self._generate_protobuf()
        app_request.sendTeamMessage.CopyFrom(app_send_message)

        self.remote.ignored_responses.append(app_request.seq)

        await self.remote.send_message(app_request)

    async def get_info(self) -> RustInfo:

        await self._handle_ratelimit()

        app_request = self._generate_protobuf()
        app_request.getInfo.CopyFrom(AppEmpty())

        await self.remote.send_message(app_request)

        response = await self.remote.get_response(app_request.seq, app_request)

        return RustInfo(response.response.info)

    async def get_team_chat(self) -> List[RustChatMessage]:

        await self._handle_ratelimit()

        app_request = self._generate_protobuf()
        app_request.getTeamChat.CopyFrom(AppEmpty())

        await self.remote.send_message(app_request)

        messages = (
            await self.remote.get_response(app_request.seq, app_request)
        ).response.teamChat.messages

        return [RustChatMessage(message) for message in messages]

    async def get_team_info(self) -> RustTeamInfo:

        await self._handle_ratelimit()

        app_request = self._generate_protobuf()
        app_request.getTeamInfo.CopyFrom(AppEmpty())

        await self.remote.send_message(app_request)

        app_message = await self.remote.get_response(app_request.seq, app_request)

        return RustTeamInfo(app_message.response.teamInfo)

    async def get_markers(self) -> List[RustMarker]:

        await self._handle_ratelimit()

        app_request = self._generate_protobuf()
        app_request.getMapMarkers.CopyFrom(AppEmpty())

        await self.remote.send_message(app_request)

        app_message = await self.remote.get_response(app_request.seq, app_request)

        return [
            RustMarker(marker) for marker in app_message.response.mapMarkers.markers
        ]

    async def get_raw_map_data(self) -> RustMap:

        await self._handle_ratelimit(5)

        app_request = self._generate_protobuf()
        app_request.getMap.CopyFrom(AppEmpty())

        await self.remote.send_message(app_request)

        app_message = await self.remote.get_response(app_request.seq, app_request)

        return RustMap(app_message.response.map)

    async def get_map(
        self,
        add_icons: bool = False,
        add_events: bool = False,
        add_vending_machines: bool = False,
        override_images: dict = None,
        add_grid: bool = False,
    ) -> Image:

        if override_images is None:
            override_images = {}

        map_size = int((await self.get_info()).size)

        await self._handle_ratelimit(
            5
            + (
                1
                if [add_icons, add_events, add_vending_machines].count(True) >= 1
                else 0
            )
        )

        app_request = self._generate_protobuf()
        app_request.getMap.CopyFrom(AppEmpty())

        await self.remote.send_message(app_request)

        app_message = await self.remote.get_response(app_request.seq, app_request)

        game_map = app_message.response.map
        monuments = list(game_map.monuments)

        try:
            image = Image.open(BytesIO(game_map.jpgImage))
        except Exception:
            raise ImageError("Invalid bytes for the image")

        if not self.use_test_server:
            image = image.crop((500, 500, game_map.height - 500, game_map.width - 500))

        game_map = image.resize((map_size, map_size), Image.ANTIALIAS).convert("RGBA")

        if add_grid:
            grid = Image.open(
                requests.get(
                    f"https://files.rustmaps.com/grids/{map_size}.png", stream=True
                ).raw
            ).resize((map_size, map_size), Image.ANTIALIAS).convert("RGBA")

            game_map.paste(grid, (0, 0), grid)

        if add_icons or add_events or add_vending_machines:
            map_markers = (
                await self.get_markers() if add_events or add_vending_machines else []
            )

            if add_icons:
                for monument in monuments:
                    if str(monument.token) == "DungeonBase":
                        continue
                    icon = convert_monument(monument.token, override_images)
                    if monument.token in override_images:
                        icon = icon.resize((150, 150))
                    if str(monument.token) == "train_tunnel_display_name":
                        icon = icon.resize((100, 125))
                    game_map.paste(
                        icon,
                        (format_coord(int(monument.x), int(monument.y), map_size)),
                        icon,
                    )

            if add_vending_machines:
                with resources.path(
                    "rustplus.api.icons", "vending_machine.png"
                ) as path:
                    vending_machine = Image.open(path).convert("RGBA")
                    vending_machine = vending_machine.resize((100, 100))

            for marker in map_markers:
                if add_events:
                    if (
                        marker.type == 2
                        or marker.type == 4
                        or marker.type == 5
                        or marker.type == 6
                        or marker.type == 8
                    ):
                        icon = convert_marker(str(marker.type), marker.rotation)
                        if marker.type == 6:
                            x = marker.x
                            y = marker.y
                            if y > map_size:
                                y = map_size
                            if y < 0:
                                y = 100
                            if x > map_size:
                                x = map_size - 75
                            if x < 0:
                                x = 50
                            game_map.paste(icon, (int(x), map_size - int(y)), icon)
                        else:
                            game_map.paste(
                                icon,
                                (format_coord(int(marker.x), int(marker.y), map_size)),
                                icon,
                            )
                if add_vending_machines and marker.type == 3:
                    game_map.paste(
                        vending_machine,
                        (int(marker.x) - 50, map_size - int(marker.y) - 50),
                        vending_machine,
                    )

        return game_map.resize((2000, 2000), Image.ANTIALIAS)

    async def get_entity_info(self, eid: int = None) -> RustEntityInfo:

        await self._handle_ratelimit()

        if eid is None:
            raise ValueError("EID cannot be None")

        app_request = self._generate_protobuf()
        app_request.entityId = eid
        app_request.getEntityInfo.CopyFrom(AppEmpty())

        await self.remote.send_message(app_request)

        app_message = await self.remote.get_response(app_request.seq, app_request)

        return RustEntityInfo(app_message.response.entityInfo)

    async def _update_smart_device(self, eid: int, value: bool) -> None:

        await self._handle_ratelimit()

        entity_value = AppSetEntityValue()
        entity_value.value = value

        app_request = self._generate_protobuf()

        app_request.entityId = eid
        app_request.setEntityValue.CopyFrom(entity_value)

        self.remote.ignored_responses.append(app_request.seq)

        await self.remote.send_message(app_request)

    async def turn_on_smart_switch(self, eid: int = None) -> None:

        if eid is None:
            raise ValueError("EID cannot be None")

        await self._update_smart_device(eid, True)

    async def turn_off_smart_switch(self, eid: int = None) -> None:

        if eid is None:
            raise ValueError("EID cannot be None")

        await self._update_smart_device(eid, False)

    async def promote_to_team_leader(self, steam_id: int = None) -> None:

        if steam_id is None:
            raise ValueError("SteamID cannot be None")

        await self._handle_ratelimit()

        leader_packet = AppPromoteToLeader()
        leader_packet.steamId = steam_id

        app_request = self._generate_protobuf()
        app_request.promoteToLeader.CopyFrom(leader_packet)

        self.remote.ignored_responses.append(app_request.seq)

        await self.remote.send_message(app_request)

    async def get_current_events(self) -> List[RustMarker]:

        return [
            marker
            for marker in (await self.get_markers())
            if marker.type == 2
            or marker.type == 4
            or marker.type == 5
            or marker.type == 6
            or marker.type == 8
        ]

    async def get_contents(
        self, eid: int = None, combine_stacks: bool = False
    ) -> RustContents:

        if eid is None:
            raise ValueError("EID cannot be None")

        returned_data = await self.get_entity_info(eid)

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

    @deprecated("Use RustSocket.get_contents")
    async def get_tc_storage_contents(
        self, eid: int = None, combine_stacks: bool = False
    ) -> RustContents:
        return await self.get_contents(eid=eid, combine_stacks=combine_stacks)
