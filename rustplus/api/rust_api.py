from typing import List

from .base_rust_api import BaseRustSocket
from ..commands import CommandOptions
from ..utils import *
from .structures import RustTime, RustInfo, RustMap, RustMarker, RustChatMessage, RustTeamInfo, RustTeamMember, RustTeamNote, RustEntityInfo, RustContents, RustItem
from .remote.rustproto import *

class RustSocket(BaseRustSocket):

    def __init__(self, ip: str = None, port: str = None, steamid: int = None, playertoken: int = None, command_options : CommandOptions = None, ratelimit_limit : int = 25, ratelimit_refill : int = 3) -> None:
        super().__init__(ip=ip, port=port, steamid=steamid, playertoken=playertoken, command_options=command_options, ratelimit_limit=ratelimit_limit, ratelimit_refill=ratelimit_refill)

    async def get_time(self) -> RustTime:
        
        self._handle_ratelimit()
        
        app_request = self._generate_protobuf()
        app_request.getTime.CopyFrom(AppEmpty())

        await self.ws.send_message(app_request)

        response = await self.ws.get_response(app_request.seq)

        return format_time(response)

    async def send_team_message(self, message: str) -> None:
        
        self._handle_ratelimit(2)

        app_send_message = AppSendMessage()
        app_send_message.message = message

        app_request = self._generate_protobuf()
        app_request.sendTeamMessage.CopyFrom(app_send_message)

        self.ws.ignored_responses.append(app_request.seq)

        await self.ws.send_message(app_request)

    async def get_info(self) -> RustInfo:
        
        self._handle_ratelimit()

        app_request = self._generate_protobuf()
        app_request.getInfo.CopyFrom(AppEmpty())

        await self.ws.send_message(app_request)

        response = await self.ws.get_response(app_request.seq)

        return RustInfo(response.response.info)

    async def get_team_chat(self) -> List[RustChatMessage]:
        
        self._handle_ratelimit()

        app_request = self._generate_protobuf()
        app_request.getTeamChat.CopyFrom(AppEmpty())

        await self.ws.send_message(app_request)

        messages = (await self.ws.get_response(app_request.seq)).response.teamChat.messages

        return [RustChatMessage(message) for message in messages]

    async def get_team_info(self):

        self._handle_ratelimit()

        app_request = self._generate_protobuf()
        app_request.getTeamInfo.CopyFrom(AppEmpty())

        await self.ws.send_message(app_request)

        app_message = await self.ws.get_response(app_request.seq)

        return RustTeamInfo(app_message.response.teamInfo)
    


