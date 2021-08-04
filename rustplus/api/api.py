from websocket import create_connection
from PIL import Image
from io import BytesIO
from collections import defaultdict
from datetime import datetime

from .rustplus_pb2 import *
from ..utils import *
from ..exceptions import *
from ..objects import *

class RustSocket:
    def __init__(self, ip : str, port : str, steamid : int, playertoken : int) -> None:
        
        self.seq = 1
        self.error_checker = ErrorChecker()
        self.ip = ip
        self.port = port
        self.steamid = steamid
        self.playertoken = playertoken

    def __str__(self) -> str:
        return "RustSocket: ip = {} | port = {} | steamid = {} | playertoken = {}".format(self.ip, self.port, self.steamid, self.playertoken)

    def __initProto(self) -> AppRequest:
        request = AppRequest()
        request.seq = self.seq
        self.seq += 1
        request.playerId = self.steamid
        request.playerToken = self.playertoken
        return request

    def __getTime(self) -> dict:
        request = self.__initProto()
        request.getTime.CopyFrom(AppEmpty())
        data = request.SerializeToString()

        self.ws.send_binary(data)

        return_data = self.ws.recv()

        app_message = AppMessage()
        app_message.ParseFromString(return_data)

        self.error_checker.check(app_message)

        time_parser = TimeParser()

        return {
            "DAYLENGTHMINUTES" : app_message.response.time.dayLengthMinutes,
            "SUNRISE" : time_parser.convert(app_message.response.time.sunrise),
            "SUNSET" : time_parser.convert(app_message.response.time.sunset),
            "TIME" : time_parser.convert(app_message.response.time.time)
        }

    def __getInfo(self):

        request = self.__initProto()
        request.getInfo.CopyFrom(AppEmpty())
        data = request.SerializeToString()

        self.ws.send_binary(data)

        returndata = self.ws.recv()

        appMessage = AppMessage()
        appMessage.ParseFromString(returndata)

        self.error_checker.check(appMessage)

        return appMessage

    def __getMap(self, MAPSIZE):
        request = self.__initProto()
        request.getMap.CopyFrom(AppEmpty())
        data = request.SerializeToString()

        self.ws.send_binary(data)

        return_data = self.ws.recv()

        app_message = AppMessage()
        app_message.ParseFromString(return_data)

        self.error_checker.check(app_message)

        map = app_message.response.map
        monuments = list(map.monuments)

        try:
            im = Image.open(BytesIO(map.jpgImage))
        except:
            raise ImageError("Invalid bytes for the image")

        im = im.crop((500,500,map.height-500,map.width-500))

        im = im.resize((MAPSIZE,MAPSIZE), Image.ANTIALIAS)

        return (im, monuments)

    def __getMarkers(self):

        request = self.__initProto()
        request.getMapMarkers.CopyFrom(AppEmpty())
        data = request.SerializeToString()

        self.ws.send_binary(data)

        returndata = self.ws.recv()

        appMessage = AppMessage()
        appMessage.ParseFromString(returndata)

        self.error_checker.check(appMessage)

        return appMessage

    def __getTeamChat(self):

        request = self.__initProto()
        request.getTeamChat.CopyFrom(AppEmpty())
        data = request.SerializeToString()

        self.ws.send_binary(data)

        returndata = self.ws.recv()

        appMessage = AppMessage()
        appMessage.ParseFromString(returndata)

        self.error_checker.check(appMessage)

        return appMessage

    def __sendTeamChatMessage(self, message):

        msg = AppSendMessage()
        msg.message = message

        request = self.__initProto()
        request.sendTeamMessage.CopyFrom(msg)
        data = request.SerializeToString()

        self.ws.send_binary(data)

        messageReturn = self.ws.recv()
        messageReturnAppMessage = AppMessage()
        messageReturnAppMessage.ParseFromString(messageReturn)
        if str(messageReturnAppMessage.response.error) != "":
            return messageReturnAppMessage
        
        success = self.ws.recv()

        appMessage = AppMessage()
        appMessage.ParseFromString(success)

        self.error_checker.check(appMessage)

        return appMessage

    def __getCameraFrame(self, id, frame):

        cameraPacket = AppCameraFrameRequest()
        cameraPacket.identifier = id
        cameraPacket.frame = frame

        request = self.__initProto()
        request.getCameraFrame.CopyFrom(cameraPacket)
        data = request.SerializeToString()

        self.ws.send_binary(data)

        returndata = self.ws.recv()

        appMessage = AppMessage()
        appMessage.ParseFromString(returndata)

        self.error_checker.check(appMessage)

        return appMessage

    def __getTeamInfo(self):

        request = self.__initProto()
        request.getTeamInfo.CopyFrom(AppEmpty())
        data = request.SerializeToString()

        self.ws.send_binary(data)

        returndata = self.ws.recv()

        appMessage = AppMessage()
        appMessage.ParseFromString(returndata)

        self.error_checker.check(appMessage)

        return appMessage

    def __getEntityInfo(self, eid : int): 

        request = self.__initProto()

        request.entityId = eid
        request.getEntityInfo.CopyFrom(AppEmpty())
        data = request.SerializeToString()

        self.ws.send_binary(data)

        returndata = self.ws.recv()

        appMessage = AppMessage()
        appMessage.ParseFromString(returndata)

        self.error_checker.check(appMessage)

        return appMessage

    def __updateSmartDevice(self, eid : int, value : bool) -> AppMessage:

        entityValue = AppSetEntityValue()
        entityValue.value = value

        request = self.__initProto()

        request.entityId = eid
        request.setEntityValue.CopyFrom(entityValue)

        data = request.SerializeToString()

        self.ws.send_binary(data)

        returndata = self.ws.recv()

        appMessage = AppMessage()
        appMessage.ParseFromString(returndata)

        self.error_checker.check(appMessage)
    
        return appMessage

    def __promoteToTeamLeader(self, SteamID : int):

        leaderPacket = AppPromoteToLeader()
        leaderPacket.steamId = SteamID

        request = self.__initProto()
        request.promoteToLeader.CopyFrom(leaderPacket)
        data = request.SerializeToString()

        self.ws.send_binary(data)

        returndata = self.ws.recv()

        appMessage = AppMessage()
        appMessage.ParseFromString(returndata)

        self.error_checker.check(appMessage)

        return appMessage

    def __getTCStorage(self, EID, combineStacks):
        returnedData = self.__getEntityInfo(EID)

        returnDict = {}

        targetTime = datetime.utcfromtimestamp(int(returnedData.response.entityInfo.payload.protectionExpiry))
        difference = targetTime - datetime.utcnow()

        returnDict["protectionTime"] = difference
        returnDict["hasProtection"] = bool(returnedData.response.entityInfo.payload.hasProtection)

        returnItems = list(returnedData.response.entityInfo.payload.items)

        idConverter = IdToName()

        items = []

        for item in returnItems:
            items.append(Storage_Item(idConverter.translate(item.itemId), item.itemId, item.quantity, item.itemIsBlueprint))

        if not combineStacks:
            returnDict["contents"] = items
            return returnDict

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
            items.append(Storage_Item(idConverter.translate(key), key, int(mergedMap[key][0]), bool(mergedMap[key][1])))

        returnDict["contents"] = items
        return returnDict

    def __getCurrentEvents(self):

        mapMarkers = list(self.__getMarkers().response.mapMarkers.markers)
        poi = []
        for marker in mapMarkers:
            if marker.type == 2 or marker.type == 4 or marker.type == 5 or marker.type == 6:
                poi.append(marker)
        return poi

    ################################################

    def connect(self) -> None:
        """
        Connect to the Rust Server
        """
        try:
            self.ws = create_connection("ws://{}:{}".format(self.ip,self.port))
        except:
            raise ServerNotResponsiveError("The sever is not available to connect to - your ip/port are either correct or the server is offline")

    def closeConnection(self) -> None:
        """
        Close the connection to the Rust Server
        """
        self.ws.abort()

    def disconnect(self) -> None:
        """
        Close the connection to the Rust Server
        """
        self.closeConnection()

    def getTime(self) -> dict:
        """
        Gets the current in-game time
        """
        return self.__getTime()

    def getInfo(self) -> dict:
        """
        Gets information on the Rust Server
        """
        data = self.__getInfo().response.info

        outData = {}   

        outData["url"] = data.url
        outData["name"] = data.name
        outData["map"] = data.map
        outData["size"] = data.mapSize
        outData["currentPlayers"] = data.players
        outData["maxPlayers"] = data.maxPlayers
        outData["queuedPlayers"] = data.queuedPlayers
        outData["seed"] = data.seed

        return outData

    def getMap(self, addicons : bool = False) -> Image:
        """
        Returns the Map of the server with the option to add icons.
        """
        MAPSIZE = int(self.__getInfo().response.info.mapSize)

        map, monuments = self.__getMap(MAPSIZE)

        if addicons:
            monument_name_converter = MonumentNameToImage()
            cood_formatter = CoordUtil()
            for monument in monuments:
                icon = monument_name_converter.convert(monument.token)
                map.paste(icon, (cood_formatter.format(int(monument.x), int(monument.y), MAPSIZE)), icon)

        map = map.resize((2000, 2000), Image.ANTIALIAS)

        return map

    def getMarkers(self) -> list:
        """
        Gets the map markers for the server. Returns a list of them
        """
        
        markers = self.__getMarkers()

        return markers.response.mapMarkers

    def getTeamChat(self) -> list:
        """
        Returns a list of chat messages, formatted as 'ChatMessage' objects with entries:
        - steamID, 
        - senderName,
        - message, 
        - colour
        """

        chat = self.__getTeamChat()

        messages = chat.response.teamChat.messages

        messagesToReturn = []

        for i in range(0,len(messages)-1):
            currentMessage = messages[i]
            messagesToReturn.append(ChatMessage(currentMessage.steamId,currentMessage.name,currentMessage.message,currentMessage.color))

        return messagesToReturn

    def sendTeamMessage(self, message : str) -> AppMessage:
        """
        Sends a team chat message as yourself. Returns the success data back from the server. Can be ignored
        """

        data = self.__sendTeamChatMessage(message)
        return data

    def getCameraFrame(self, id : str, frame : int) -> Image:
        """
        Returns a low quality jpeg image from a camera in-game
        """

        returnData = self.__getCameraFrame(id,frame)

        try:
            image = Image.open(BytesIO(returnData.response.cameraFrame.jpgImage))
        except:
            raise ImageError("Invalid Bytes Recieved")

        return image

    def getTeamInfo(self) -> AppTeamInfo:
        """
        Returns an AppTeamInfo object of the players in your team, as well as a lot of data about them
        """

        teamInfo = self.__getTeamInfo()

        return teamInfo.response.teamInfo

    def turnOnSmartSwitch(self, EID : int) -> AppMessage:
        """
        Turns on a smart switch on the server
        """

        return self.__updateSmartDevice(EID, True)

    def turnOffSmartSwitch(self, EID : int) -> AppMessage:
        """
        Turns off a smart switch on the server
        """

        return self.__updateSmartDevice(EID, False)

    def getEntityInfo(self, EID : int) -> AppEntityInfo: 
        """
        Get the entity info from a given entity ID
        """
        data = self.__getEntityInfo(EID)

        return data.response.entityInfo

    def promoteToTeamLeader(self, SteamID : int) -> AppMessage:
        """
        Promotes a given user to the team leader by their 64-bit Steam ID
        """

        return self.__promoteToTeamLeader(SteamID)

    def getTCStorageContents(self, EID : int, combineStacks : bool = False) -> dict:
        """
        Gets the Information about TC Upkeep and Contents.
        Do not use this for any other storage monitor than a TC
        """
        
        return self.__getTCStorage(EID, combineStacks)

    def getCurrentEvents(self) -> list:
        """
        Gets all current ongoing events on the map
        Can detect:
            - Explosion
            - CH47 (Chinook)
            - Cargo Ship
            - Locked Crate

        Returns the MapMarker for the event
        """
        
        return self.__getCurrentEvents()