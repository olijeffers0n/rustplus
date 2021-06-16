import io
import PIL
from PIL import Image
from websocket import create_connection

from . import rustplus_pb2
from ..exceptions import ClientError, ImageError
from ..objects import ChatMessage

from importlib import resources

nametoFile = {
    "train_tunnel_display_name" : "train.png",
    "supermarket" : "supermarket.png",
    "mining_outpost_display_name" : "mining_outpost.png",
    "gas_station" : "oxums.png",
    "fishing_village_display_name" : "fishing.png",
    "large_fishing_village_display_name" : "fishing.png",
    "lighthouse_display_name" : "lighthouse.png",
    "excavator" : "excavator.png",
    "water_treatment_plant_display_name" : "water_treatment.png",
    "train_yard_display_name" : "train_yard.png",
    "outpost" : "outpost.png",
    "bandit_camp" : "bandit.png",
    "junkyard_display_name" : "junkyard.png",
    "dome_monument_name" : "dome.png",
    "satellite_dish_display_name" : "satellite.png",
    "power_plant_display_name" : "power_plant.png",
    "military_tunnels_display_name" : "military_tunnels.png",
    "airfield_display_name" : "airfield.png",
    "launchsite" : "launchsite.png",
    "sewer_display_name" : "sewer.png",
    "oil_rig_small" : "small_oil_rig.png",
    "large_oil_rig" : "large_oil_rig.png"
}

class RustSocket:

    def __init__(self, ip, port, playerId, playerToken):

        self.seq = 1
        self.playerId = playerId
        self.playerToken = playerToken
        self.ip = ip
        self.port = port


    def connect(self):
        self.ws = create_connection("ws://{}:{}".format(self.ip,self.port))


    def closeConnection(self):
        self.ws.abort()


    def __errorCheck(self, response):
        if response.response.error.error != "":
            raise ClientError("An Error has been returned: {}".format(str(response.response.error.error)))


    def __getTime(self):

        request = rustplus_pb2.AppRequest()
        request.seq = self.seq
        self.seq += 1
        request.playerId = self.playerId
        request.playerToken = self.playerToken
        request.getTime.CopyFrom(rustplus_pb2.AppEmpty())
        data = request.SerializeToString()

        self.ws.send_binary(data)

        returndata = self.ws.recv()

        appMessage = rustplus_pb2.AppMessage()
        appMessage.ParseFromString(returndata)

        self.__errorCheck(appMessage)
        
        input = float(appMessage.response.time.time) 
        secondsGone = input * 60
        mins = int(secondsGone // 60)
        seconds = int(secondsGone % 60)
        if len(str(seconds)) == 1:
            timeString = str(mins) + ":0" + str(seconds)
        else:
            timeString = str(mins) + ":" + str(seconds)

        return timeString


    def __getMap(self):

        request = rustplus_pb2.AppRequest()
        request.seq = self.seq
        self.seq += 1
        request.playerId = self.playerId
        request.playerToken = self.playerToken
        request.getMap.CopyFrom(rustplus_pb2.AppEmpty())
        data = request.SerializeToString()

        self.ws.send_binary(data)

        returndata = self.ws.recv()

        appMessage = rustplus_pb2.AppMessage()
        appMessage.ParseFromString(returndata)

        self.__errorCheck(appMessage)
   
        return appMessage.response.map


    def __formatCoords(self, x : int, y : int, mapSize : int):

        y = mapSize - y - 100
        x -= 100

        if x < 0:
            x = 0
        if x > mapSize:
            x = mapSize - 200
        if y < 0:
            y = 0
        if y > mapSize:
            y = mapSize-200

        return (int(x),int(y))


    def __getMarkers(self):

        request = rustplus_pb2.AppRequest()
        request.seq = self.seq
        self.seq += 1
        request.playerId = self.playerId
        request.playerToken = self.playerToken
        request.getMapMarkers.CopyFrom(rustplus_pb2.AppEmpty())
        data = request.SerializeToString()

        self.ws.send_binary(data)

        returndata = self.ws.recv()

        appMessage = rustplus_pb2.AppMessage()
        appMessage.ParseFromString(returndata)

        self.__errorCheck(appMessage)

        return appMessage


    def __getInfo(self):

        request = rustplus_pb2.AppRequest()
        request.seq = self.seq
        self.seq += 1
        request.playerId = self.playerId
        request.playerToken = self.playerToken
        request.getInfo.CopyFrom(rustplus_pb2.AppEmpty())
        data = request.SerializeToString()

        self.ws.send_binary(data)

        returndata = self.ws.recv()

        appMessage = rustplus_pb2.AppMessage()
        appMessage.ParseFromString(returndata)

        self.__errorCheck(appMessage)

        return appMessage


    def __getTeamChat(self):

        request = rustplus_pb2.AppRequest()
        request.seq = self.seq
        self.seq += 1
        request.playerId = self.playerId
        request.playerToken = self.playerToken
        request.getTeamChat.CopyFrom(rustplus_pb2.AppEmpty())
        data = request.SerializeToString()

        self.ws.send_binary(data)

       
        returndata = self.ws.recv()

        appMessage = rustplus_pb2.AppMessage()
        appMessage.ParseFromString(returndata)

        self.__errorCheck(appMessage)

        return appMessage


    def __sendTeamChatMessage(self, message):

        msg = rustplus_pb2.AppSendMessage()
        msg.message = message

        request = rustplus_pb2.AppRequest()
        request.seq = self.seq
        self.seq += 1
        request.playerId = self.playerId
        request.playerToken = self.playerToken
        request.sendTeamMessage.CopyFrom(msg)
        data = request.SerializeToString()

        self.ws.send_binary(data)

        messageReturn = self.ws.recv()
        success = self.ws.recv()

        appMessage = rustplus_pb2.AppMessage()
        appMessage.ParseFromString(success)
            
        self.__errorCheck(appMessage)

        return appMessage


    def __getCameraFrame(self, id, frame):

        cameraPacket = rustplus_pb2.AppCameraFrameRequest()
        cameraPacket.identifier = id
        cameraPacket.frame = frame

        request = rustplus_pb2.AppRequest()
        request.seq = self.seq
        self.seq += 1
        request.playerId = self.playerId
        request.playerToken = self.playerToken
        request.getCameraFrame.CopyFrom(cameraPacket)
        data = request.SerializeToString()

        self.ws.send_binary(data)


        returndata = self.ws.recv()

        appMessage = rustplus_pb2.AppMessage()
        appMessage.ParseFromString(returndata)


        self.__errorCheck(appMessage)

        return appMessage


    def __getTeamInfo(self):

        request = rustplus_pb2.AppRequest()
        request.seq = self.seq
        self.seq += 1
        request.playerId = self.playerId
        request.playerToken = self.playerToken
        request.getTeamInfo.CopyFrom(rustplus_pb2.AppEmpty())
        data = request.SerializeToString()

        self.ws.send_binary(data)

        returndata = self.ws.recv()

        appMessage = rustplus_pb2.AppMessage()
        appMessage.ParseFromString(returndata)

        self.__errorCheck(appMessage)

        return appMessage


    def __updateSmartDevice(self, eid : int, value : bool) -> rustplus_pb2.AppMessage:

        entityValue = rustplus_pb2.AppSetEntityValue()
        entityValue.value = value

        request = rustplus_pb2.AppRequest()
        request.seq = self.seq
        self.seq += 1
        request.playerId = self.playerId
        request.playerToken = self.playerToken

        request.entityId = eid
        request.setEntityValue.CopyFrom(entityValue)

        data = request.SerializeToString()

        self.ws.send_binary(data)

        returndata = self.ws.recv()

        appMessage = rustplus_pb2.AppMessage()
        appMessage.ParseFromString(returndata)
            
        self.__errorCheck(appMessage)

        return appMessage


    def __getEntityInfo(self, eid : int): 

        request = rustplus_pb2.AppRequest()
        request.seq = self.seq
        self.seq += 1
        request.playerId = self.playerId
        request.playerToken = self.playerToken
        request.entityId = eid
        request.getEntityInfo.CopyFrom(rustplus_pb2.AppEmpty())
        data = request.SerializeToString()

        self.ws.send_binary(data)

        returndata = self.ws.recv()

        appMessage = rustplus_pb2.AppMessage()
        appMessage.ParseFromString(returndata)

        self.__errorCheck(appMessage)

        return appMessage

#######################FRONT FACING##############################

    def getTeamInfo(self) -> list:
        """
        Returns a list of the players in your team, as well as a lot of data about them
        """

        teamInfo = self.__getTeamInfo()

        return teamInfo.response.teamInfo


    def getCameraFrame(self, id : str, frame : int) -> Image:
        """
        Returns a low quality image from a camera in-game
        """

        returnData = self.__getCameraFrame(id,frame)

        try:
            image = PIL.Image.open(io.BytesIO(returnData.response.cameraFrame.jpgImage))
        except:
            raise ImageError("Invalid Bytes Recieved")

        return image


    def sendTeamMessage(self, message : str):
        """
        Sends a team chat message as yourself. Returns the success data back from the server. Can be ignored
        """

        data = self.__sendTeamChatMessage(message)
        return data.response


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


    def getMap(self, addIcons : bool = True) -> Image:
        """
        Gets the image of the map. Argument 'addIcons' decides whether to add monument icons. Defaults to True
        """
        
        map = self.__getMap()
        info = self.__getInfo()

        # Gets the Mapsize as well as all the monuments

        mapSize  = int(info.response.info.mapSize)
        monuments = list(map.monuments)

        #Converts the bytes to an Image
        try:
            im = PIL.Image.open(io.BytesIO(map.jpgImage))
        except:
            raise ImageError("Invalid bytes for the image")

        #Crops out the ocean border
        im1 = im.crop((500,500,map.height-500,map.width-500))

        #Resizes the image so that it is the same dimensions as the in-game map
        im2 = im1.resize((mapSize,mapSize), Image.ANTIALIAS)

        #Instanciates the image to paste to
        copied = im2.copy()

        if addIcons:

            #Loop through each monument
            for monument in monuments:

                if monument.token in nametoFile:
                    file_name = nametoFile[monument.token]
                    with resources.path("rustplus.api.icons", file_name) as path:
                        icon = Image.open(path).convert("RGBA")
                elif "mining_quarry" in monument.token or "harbor" in monument.token or "stables" in monument.token or "swamp" in monument.token:
                    if "mining_quarry" in monument.token:
                        file_name = "quarry.png"
                    elif "harbor" in monument.token:
                        file_name = "harbour.png"
                    elif "stables" in monument.token:
                        file_name = "stable.png"
                    elif "swamp" in monument.token:
                        file_name = "swamp.png"
                    with resources.path("rustplus.api.icons", file_name) as path:
                        icon = Image.open(path).convert("RGBA")
                else:
                    print(monument.token + " - Has no icon, defaulting...")
                    with resources.path("rustplus.api.icons", "icon.png") as path:
                        icon = Image.open(path).convert("RGBA")

                copied.paste(icon,(self.__formatCoords(monument.x, monument.y, mapSize)), icon)

        copied = copied.resize((2000,2000), Image.ANTIALIAS)

        return copied


    def getInfo(self) -> dict:
        """
        Returns a dictionary of key information from the server
        """

        data = self.__getInfo()

        outData = {}   

        outData["url"] = data.response.info.url
        outData["name"] = data.response.info.name
        outData["map"] = data.response.info.map
        outData["size"] = data.response.info.mapSize
        outData["currentPlayers"] = data.response.info.players
        outData["maxPlayers"] = data.response.info.maxPlayers
        outData["queuedPlayers"] = data.response.info.queuedPlayers
        outData["seed"] = data.response.info.seed

        return outData


    def getTime(self) -> str:
        """
        Gets the Current time and formats it to "HOURS:MINTUES"
        """

        time = self.__getTime()

        return time

    
    def getMarkers(self) -> list:
        """
        Gets the map markers for the server. Returns a list of them
        """
        
        markers = self.__getMarkers()

        return markers.response.mapMarkers


    def turnOnSmartSwitch(self, EID : int):
        """
        Turns on a smart switch on the server
        """

        return self.__updateSmartDevice(EID, True)


    def turnOffSmartSwitch(self, EID : int):
        """
        Turns off a smart switch on the server
        """

        return self.__updateSmartDevice(EID, False)

    
    def getEntityInfo(self, EID : int) -> rustplus_pb2.AppEntityInfo: 

        data = self.__getEntityInfo(EID)

        return data.response.entityInfo
