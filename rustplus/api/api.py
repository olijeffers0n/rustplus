from typing import List
from websocket import create_connection, WebSocketConnectionClosedException
from PIL import Image
from io import BytesIO
from collections import defaultdict
from datetime import datetime
from importlib import resources
import threading
import asyncio

from .rustplus_pb2 import *
from .structures import RustTime, RustInfo, RustMap, RustMarker, RustChatMessage, RustSuccess, RustTeamInfo, RustTeamMember, RustTeamNote, RustEntityInfo, RustContents, RustItem
from ..utils import MonumentNameToImage, TimeParser, CoordUtil, ErrorChecker, IdToName, MapMarkerConverter
from ..exceptions import ImageError, ServerNotResponsiveError, ClientNotConnectedError
from ..commands import CommandOptions, RustCommandHandler

class RustSocket:
    def __init__(self, ip : str, port : str, steamid : int, playertoken : int, command_options : CommandOptions = None) -> None:
        
        self.seq = 1
        self.ip = ip
        self.port = port
        self.steamid = steamid
        self.playertoken = playertoken
        self.error_checker = ErrorChecker()
        self.responses = {}
        self.ignored_responses = []

        if command_options is not None:
            self.prefix = command_options.prefix

            self.command_handler = RustCommandHandler(command_options)
            
        self.ws = None

    def __str__(self) -> str:
        return "RustSocket[ip = {} | port = {} | steamid = {} | playertoken = {}]".format(self.ip, self.port, self.steamid, self.playertoken)

    def __initProto(self) -> AppRequest:
        request = AppRequest()
        request.seq = self.seq
        self.seq += 1
        request.playerId = self.steamid
        request.playerToken = self.playertoken
        return request

    def __start_listener(self) -> None:

        loop = asyncio.new_event_loop()

        loop.run_until_complete(self.__listener())
        loop.close()

    async def __listener(self) -> None:

        while self.ws != None:

            try:

                data = self.ws.recv()

                app_message = AppMessage()
                app_message.ParseFromString(data)

                if app_message.broadcast.teamMessage.message.message == "":
                    if app_message.response.seq not in self.ignored_responses:
                        self.responses[app_message.response.seq] = app_message
                else:
                    message = RustChatMessage(app_message.broadcast.teamMessage.message)
                    
                    if message.message.startswith(self.prefix):
                        await self.command_handler.run_command(message=message)
                    
            except WebSocketConnectionClosedException:
                return

    async def __getResponse(self, seq):

        while seq not in self.responses:
            await asyncio.sleep(0.1)
        response = self.responses[seq]
        del self.responses[seq]
        return response

    async def __sendAndRecieve(self, request, response = True) -> AppMessage:

        data = request.SerializeToString()

        if self.ws == None:
            raise ClientNotConnectedError("Not Connected")

        self.ws.send_binary(data)

        if response:

            app_message = await self.__getResponse(request.seq)

            await self.error_checker.check(app_message)

            return app_message

        return None

    async def __getTime(self) -> RustTime:

        request = self.__initProto()
        request.getTime.CopyFrom(AppEmpty())

        time = (await self.__sendAndRecieve(request)).response.time

        time_parser = TimeParser()

        return RustTime(time.dayLengthMinutes, time_parser.convert(time.sunrise), time_parser.convert(time.sunset), time_parser.convert(time.time))

    async def __getInfo(self) -> RustInfo:

        request = self.__initProto()
        request.getInfo.CopyFrom(AppEmpty())
        
        app_message = await self.__sendAndRecieve(request)

        return RustInfo(app_message.response.info)

    async def __getMap(self, MAPSIZE):

        request = self.__initProto()
        request.getMap.CopyFrom(AppEmpty())
        
        app_message = await self.__sendAndRecieve(request)

        map = app_message.response.map
        monuments = list(map.monuments)

        try:
            im = Image.open(BytesIO(map.jpgImage))
        except:
            raise ImageError("Invalid bytes for the image")

        im = im.crop((500,500,map.height-500,map.width-500))

        im = im.resize((MAPSIZE,MAPSIZE), Image.ANTIALIAS)

        return (im, monuments)

    async def __getAndFormatMap(self, addIcons : bool, addEvents : bool, addVendingMachines : bool, overrideImages : dict = {}):

        MAPSIZE = int((await self.__getInfo()).size)

        map, monuments = await self.__getMap(MAPSIZE)

        if addIcons or addEvents or addVendingMachines:
            mapMarkers = await self.__getMarkers()
            cood_formatter = CoordUtil()

            if addIcons:
                monument_name_converter = MonumentNameToImage(overrideImages)
                for monument in monuments:
                    if str(monument.token) == "DungeonBase":
                        continue
                    icon = monument_name_converter.convert(monument.token)
                    icon = icon.resize((150, 150))
                    if str(monument.token) == "train_tunnel_display_name":
                        icon = icon.resize((100, 125))
                    map.paste(icon, (cood_formatter.format(int(monument.x), int(monument.y), MAPSIZE)), icon)

            if addVendingMachines:
                with resources.path("rustplus.api.icons", "vending_machine.png") as path:
                    vendingMachine = Image.open(path).convert("RGBA")
                    vendingMachine = vendingMachine.resize((100, 100))

            for marker in mapMarkers:
                if addEvents:
                    markerConverter = MapMarkerConverter()
                    if marker.type == 2 or marker.type == 4 or marker.type == 5 or marker.type == 6:
                        icon = markerConverter.convert(str(marker.type), marker.rotation)
                        if marker.type == 6:
                            x = marker.x
                            y = marker.y
                            if y > MAPSIZE: y = MAPSIZE
                            if y < 0: y = 100
                            if x > MAPSIZE: x = MAPSIZE - 75
                            if x < 0: x = 50
                            map.paste(icon, (int(x), MAPSIZE - int(y)), icon)
                        else:
                            map.paste(icon, (cood_formatter.format(int(marker.x), int(marker.y), MAPSIZE)), icon)
                if addVendingMachines and marker.type == 3:
                        map.paste(vendingMachine, (int(marker.x) - 50, MAPSIZE - int(marker.y) - 50), vendingMachine)

        return map.resize((2000, 2000), Image.ANTIALIAS)

    async def __getRawMapData(self) -> RustMap: 

        request = self.__initProto()
        request.getMap.CopyFrom(AppEmpty())
        
        app_message = (await self.__sendAndRecieve(request)).response.map

        return RustMap(app_message)

    async def __getMarkers(self) -> List[RustMarker]:

        request = self.__initProto()
        request.getMapMarkers.CopyFrom(AppEmpty())

        markers = (await self.__sendAndRecieve(request)).response.mapMarkers

        return [RustMarker(marker) for marker in markers.markers]

    async def __getTeamChat(self):

        request = self.__initProto()
        request.getTeamChat.CopyFrom(AppEmpty())
        
        messages = (await self.__sendAndRecieve(request)).response.teamChat.messages

        return [RustChatMessage(message) for message in messages]

    async def __sendTeamChatMessage(self, message) -> RustSuccess:

        msg = AppSendMessage()
        msg.message = message

        request = self.__initProto()
        request.sendTeamMessage.CopyFrom(msg)

        self.ignored_responses.append(request.seq)
        await self.__sendAndRecieve(request, False)

        return RustSuccess(0,"Success")

    async def __getCameraFrame(self, id, frame):

        cameraPacket = AppCameraFrameRequest()
        cameraPacket.identifier = id
        cameraPacket.frame = frame

        request = self.__initProto()
        request.getCameraFrame.CopyFrom(cameraPacket)

        app_message = await self.__sendAndRecieve(request)

        return app_message

    async def __getTeamInfo(self):

        request = self.__initProto()
        request.getTeamInfo.CopyFrom(AppEmpty())

        app_message = await self.__sendAndRecieve(request)

        return RustTeamInfo(app_message.response.teamInfo)

    async def __getEntityInfo(self, eid : int) -> RustEntityInfo: 

        request = self.__initProto()

        request.entityId = eid
        request.getEntityInfo.CopyFrom(AppEmpty())
        
        return RustEntityInfo((await self.__sendAndRecieve(request)).response.entityInfo)

    async def __updateSmartDevice(self, eid : int, value : bool) -> AppMessage:

        entityValue = AppSetEntityValue()
        entityValue.value = value

        request = self.__initProto()

        request.entityId = eid
        request.setEntityValue.CopyFrom(entityValue)

        app_message = await self.__sendAndRecieve(request)

        return RustSuccess(app_message.response.seq, app_message.response.success)

    async def __promoteToTeamLeader(self, SteamID : int):

        leaderPacket = AppPromoteToLeader()
        leaderPacket.steamId = SteamID

        request = self.__initProto()
        request.promoteToLeader.CopyFrom(leaderPacket)
        
        app_message = await self.__sendAndRecieve(request)

        return RustSuccess(app_message.response.seq, app_message.response.success)

    async def __getTCStorage(self, EID, combineStacks):

        returnedData = await self.__getEntityInfo(EID)

        targetTime = datetime.utcfromtimestamp(int(returnedData.protectionExpiry))
        difference = targetTime - datetime.utcnow()

        idConverter = IdToName()

        items = []

        for item in returnedData.items:
            items.append(RustItem(idConverter.translate(item.itemId), item.itemId, item.quantity, item.itemIsBlueprint))

        if combineStacks:
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
                items.append(RustItem(idConverter.translate(key), key, int(mergedMap[key][0]), bool(mergedMap[key][1])))

        return RustContents(difference, bool(returnedData.hasProtection), items)

    async def __getCurrentEvents(self):

        return [marker for marker in (await self.__getMarkers()) if marker.type == 2 or marker.type == 4 or marker.type == 5 or marker.type == 6]

    ################################################

    async def connect(self) -> None:
        """
        Connect to the Rust Server
        """
        try:
            self.ws = create_connection("ws://{}:{}".format(self.ip,self.port))
        except:
            raise ServerNotResponsiveError("The sever is not available to connect to - your ip/port are either correct or the server is offline")

        threading.Thread(target=self.__start_listener).start()

    async def closeConnection(self) -> None:
        """
        Close the connection to the Rust Server
        """
        self.ws.abort()
        self.ws = None

    async def disconnect(self) -> None:
        """
        Close the connection to the Rust Server
        """
        await self.closeConnection()

    async def getTime(self) -> RustTime:
        """
        Gets the current in-game time
        """
        return await self.__getTime()

    async def getInfo(self) -> RustInfo:
        """
        Gets information on the Rust Server
        """
        return await self.__getInfo()

    async def getRawMapData(self) -> RustMap:
        """
        Returns the list of monuments on the server. This is a relatively expensive operation as the monuments are part of the map data
        """
        return await self.__getRawMapData()

    async def getMap(self, addIcons : bool = False, addEvents : bool = False, addVendingMachines : bool = False, overrideImages : dict = {}) -> Image:
        """
        Returns the Map of the server with the option to add icons.
        """
        return await self.__getAndFormatMap(addIcons, addEvents, addVendingMachines, overrideImages)

    async def getMarkers(self) -> List[RustMarker]:
        """
        Gets the map markers for the server. Returns a list of them
        """

        return await self.__getMarkers()

    async def getTeamChat(self) -> List[RustChatMessage]:
        """
        Returns a list of RustChatMessage objects
        """

        return await self.__getTeamChat()

    async def sendTeamMessage(self, message : str) -> RustSuccess:
        """
        Sends a team chat message as yourself. Returns the success data back from the server. Can be ignored
        """

        return await self.__sendTeamChatMessage(message)

    async def getCameraFrame(self, id : str, frame : int) -> Image:
        """
        Returns a low quality jpeg image from a camera in-game
        """

        returnData = await self.__getCameraFrame(id,frame)

        try:
            image = Image.open(BytesIO(returnData.response.cameraFrame.jpgImage))
        except:
            raise ImageError("Invalid Bytes Recieved")

        return image

    async def getTeamInfo(self) -> RustTeamInfo:
        """
        Returns an AppTeamInfo object of the players in your team, as well as a lot of data about them
        """

        return await self.__getTeamInfo()

    async def turnOnSmartSwitch(self, EID : int) -> RustSuccess:
        """
        Turns on a smart switch on the server
        """

        return await self.__updateSmartDevice(EID, True)

    async def turnOffSmartSwitch(self, EID : int) -> RustSuccess:
        """
        Turns off a smart switch on the server
        """

        return await self.__updateSmartDevice(EID, False)

    async def getEntityInfo(self, EID : int) -> RustEntityInfo: 
        """
        Get the entity info from a given entity ID
        """

        return await self.__getEntityInfo(EID)

    async def promoteToTeamLeader(self, SteamID : int) -> RustSuccess:
        """
        Promotes a given user to the team leader by their 64-bit Steam ID
        """

        return await self.__promoteToTeamLeader(SteamID)

    async def getTCStorageContents(self, EID : int, combineStacks : bool = False) -> RustContents:
        """
        Gets the Information about TC Upkeep and Contents.
        Do not use this for any other storage monitor than a TC
        """
        
        return await self.__getTCStorage(EID, combineStacks)

    async def getCurrentEvents(self) -> List[RustMarker]:
        """
        Gets all current ongoing events on the map
        Can detect:
            - Explosion
            - CH47 (Chinook)
            - Cargo Ship
            - Locked Crate

        Returns the MapMarker for the event
        """
        
        return await self.__getCurrentEvents()

    def event(self, coro) -> None:
        """A Decorator that registers an event listener"""

        self.command_handler.register_command(coro.__name__, coro)

    async def hang(self) -> None:
        """This Will permanently put your script into a state of 'hanging'. Only do this in scripts using events"""

        while True:
            await asyncio.sleep(1)
