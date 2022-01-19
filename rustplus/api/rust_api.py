import asyncio
from asyncio.futures import Future
from typing import List
from PIL import Image
from io import BytesIO
from importlib import resources
from datetime import datetime
from collections import defaultdict

from .base_rust_api import BaseRustSocket
from .structures import RustInfo, RustMap, RustMarker, RustChatMessage, RustTeamInfo, RustEntityInfo, RustContents, RustItem
from .remote.rustplus_pb2 import *
from .remote import HeartBeat
from ..commands import CommandOptions
from ..exceptions import *
from ..utils import *

class RustSocket(BaseRustSocket):

    def __init__(self, ip: str = None, port: str = None, steamid: int = None, playertoken: int = None, command_options : CommandOptions = None, raise_ratelimit_exception : bool = True, ratelimit_limit : int = 25, ratelimit_refill : int = 3) -> None:
        super().__init__(ip=ip, port=port, steamid=steamid, playertoken=playertoken, command_options=command_options, raise_ratelimit_exception=raise_ratelimit_exception, ratelimit_limit=ratelimit_limit, ratelimit_refill=ratelimit_refill, heartbeat=HeartBeat(self))

    def entity_event(self, eid):
        """
        Decorator to register a smart device listener
        """

        def wrap_func(coro): 

            def entity_event_callback(future : Future):
                try:
                    entity_info : RustEntityInfo = future.result()
                    self.remote.event_handler.register_event(eid, (coro, loop, entity_info.type))
                except:
                    raise SmartDeviceRegistrationError("Not Found")

            loop = asyncio.get_event_loop()
            future = asyncio.run_coroutine_threadsafe(self.get_entity_info(eid), loop)
            future.add_done_callback(entity_event_callback)

        return wrap_func

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

        messages = (await self.remote.get_response(app_request.seq, app_request)).response.teamChat.messages

        return [RustChatMessage(message) for message in messages]

    async def get_team_info(self):

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

        return [RustMarker(marker) for marker in app_message.response.mapMarkers.markers]

    async def get_raw_map_data(self) -> RustMap:

        await self._handle_ratelimit(5)

        app_request = self._generate_protobuf()
        app_request.getMap.CopyFrom(AppEmpty())

        await self.remote.send_message(app_request)

        app_message = await self.remote.get_response(app_request.seq, app_request)

        return RustMap(app_message.response.map)

    async def get_map(self, add_icons: bool = False, add_events: bool = False, add_vending_machines: bool = False, override_images: dict = None) -> Image:

        if override_images is None:
            override_images = {}

        MAPSIZE = int((await self.get_info()).size)
        
        await self._handle_ratelimit(5 + 1 if [add_icons, add_events, add_vending_machines].count(True) >= 1 else 0)

        app_request = self._generate_protobuf()
        app_request.getMap.CopyFrom(AppEmpty())
        
        await self.remote.send_message(app_request)

        app_message = await self.remote.get_response(app_request.seq, app_request)

        map = app_message.response.map
        monuments = list(map.monuments)

        try:
            image = Image.open(BytesIO(map.jpgImage))
        except:
            raise ImageError("Invalid bytes for the image")

        image = image.crop((500,500,map.height-500,map.width-500))

        map = image.resize((MAPSIZE,MAPSIZE), Image.ANTIALIAS)

        if add_icons or add_events or add_vending_machines:
            mapMarkers = await self.get_markers()

            if add_icons:
                for monument in monuments:
                    if str(monument.token) == "DungeonBase":
                        continue
                    icon = convert_monument(monument.token, override_images)
                    if monument.token in override_images:
                        icon = icon.resize((150, 150))
                    if str(monument.token) == "train_tunnel_display_name":
                        icon = icon.resize((100, 125))
                    map.paste(icon, (format_cood(int(monument.x), int(monument.y), MAPSIZE)), icon)

            if add_vending_machines:
                with resources.path("rustplus.api.icons", "vending_machine.png") as path:
                    vendingMachine = Image.open(path).convert("RGBA")
                    vendingMachine = vendingMachine.resize((100, 100))

            for marker in mapMarkers:
                if add_events:
                    if marker.type == 2 or marker.type == 4 or marker.type == 5 or marker.type == 6:
                        icon = convert_marker(str(marker.type), marker.rotation)
                        if marker.type == 6:
                            x = marker.x
                            y = marker.y
                            if y > MAPSIZE: y = MAPSIZE
                            if y < 0: y = 100
                            if x > MAPSIZE: x = MAPSIZE - 75
                            if x < 0: x = 50
                            map.paste(icon, (int(x), MAPSIZE - int(y)), icon)
                        else:
                            map.paste(icon, (format_cood(int(marker.x), int(marker.y), MAPSIZE)), icon)
                if add_vending_machines and marker.type == 3:
                        map.paste(vendingMachine, (int(marker.x) - 50, MAPSIZE - int(marker.y) - 50), vendingMachine)

        return map.resize((2000, 2000), Image.ANTIALIAS)
    
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

    async def _update_smart_device(self, eid : int, value : bool) -> None:

        await self._handle_ratelimit()

        entityValue = AppSetEntityValue()
        entityValue.value = value

        app_request = self._generate_protobuf()

        app_request.entityId = eid
        app_request.setEntityValue.CopyFrom(entityValue)

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

    async def promote_to_team_leader(self, steamid: int = None) -> None:
        
        if steamid is None:
            raise ValueError("SteamID cannot be None")

        await self._handle_ratelimit()

        leaderPacket = AppPromoteToLeader()
        leaderPacket.steamId = steamid

        app_request = self._generate_protobuf()
        app_request.promoteToLeader.CopyFrom(leaderPacket)
        
        self.remote.ignored_responses.append(app_request.seq)

        await self.remote.send_message(app_request)

    async def get_current_events(self) -> List[RustMarker]:
        
        return [marker for marker in (await self.get_markers()) if marker.type == 2 or marker.type == 4 or marker.type == 5 or marker.type == 6]

    async def get_tc_storage_contents(self, eid: int = None, combine_stacks: bool = False) -> RustContents:
        
        if eid is None:
            raise ValueError("EID cannot be None")

        returnedData = await self.get_entity_info(eid)

        targetTime = datetime.utcfromtimestamp(int(returnedData.protectionExpiry))
        difference = targetTime - datetime.utcnow()

        items = []

        for item in returnedData.items:
            items.append(RustItem(translate_id_to_stack(item.itemId), item.itemId, item.quantity, item.itemIsBlueprint))

        if combine_stacks:
            mergedMap = defaultdict(tuple)

            for item in items:
                data = mergedMap[str(item.itemId)]
                if data:
                    count = int(data[0]) + int(item.quantity)
                    mergedMap[str(item.itemId)] = (count, bool(item.isBlueprint))
                else:
                    mergedMap[str(item.itemId)] = (int(item.quantity), bool(item.isBlueprint))

            items = []
            for key in mergedMap.keys():
                items.append(RustItem(translate_id_to_stack(key), key, int(mergedMap[key][0]), bool(mergedMap[key][1])))

        return RustContents(difference, bool(returnedData.hasProtection), items)
