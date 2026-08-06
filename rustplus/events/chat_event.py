from rustplus.identification.handler_list import HandlerList
from ..structs import RustChatMessage

from typing import Union


class ChatEventPayload:
    HANDLER_LIST = HandlerList()

    def __init__(
        self, message: RustChatMessage, is_clan: bool, clan_id: Union[int, None]
    ) -> None:
        self._message = message
        self._is_clan = is_clan
        self._clan_id = clan_id

    @property
    def message(self) -> RustChatMessage:
        return self._message

    @property
    def is_clan(self) -> bool:
        return self._is_clan

    @property
    def clan_id(self) -> Union[int, None]:
        return self._clan_id
