from rustplus.identification.handler_list import HandlerList
from ..structs import RustClanInfo


class ClanInfoEventPayload:
    HANDLER_LIST = HandlerList()

    def __init__(self, clan_info: RustClanInfo) -> None:
        self._clan_info = clan_info

    @property
    def clan_info(self) -> RustClanInfo:
        return self._clan_info
