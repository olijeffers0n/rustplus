from .remote.rustproto import AppEmpty
from .base_rust_api import BaseRustSocket
from .structures import RustTime
from ..utils import *

class RustSocket(BaseRustSocket):

    def __init__(self, ip: str = None, port: str = None, steamid: int = None, playertoken: int = None, ratelimit_limit : int = 25, ratelimit_refill : int = 3) -> None:
        super().__init__(ip=ip, port=port, steamid=steamid, playertoken=playertoken, ratelimit_limit=ratelimit_limit, ratelimit_refill=ratelimit_refill)

    async def get_time(self) -> RustTime:
        
        self._handle_ratelimit()
        
        app_request = self._generate_protobuf()
        app_request.getTime.CopyFrom(AppEmpty())

        await self.ws.send_message(app_request)

        response = await self.ws.get_response(app_request.seq)

        return format_time(response)


