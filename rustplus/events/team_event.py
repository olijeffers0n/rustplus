from rustplus.identification.handler_list import HandlerList
from ..structs import RustTeamInfo


class TeamEventPayload:
    HANDLER_LIST = HandlerList()

    def __init__(self, player_id: int, team_info: RustTeamInfo) -> None:
        self._player_id = player_id
        self._team_info = team_info

    @property
    def player_id(self) -> int:
        return self._player_id

    @property
    def team_info(self) -> RustTeamInfo:
        return self._team_info
