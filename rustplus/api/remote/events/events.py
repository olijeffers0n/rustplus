from typing import List, Union

from ..rustplus_proto import AppMessage, AppEntityPayloadItem
from ...structures import RustChatMessage, RustClanInfo
from ...structures.rust_team_info import RustTeamInfo
from ...structures.rust_marker import RustMarker
from .handler_list import HandlerList, EntityHandlerList


class Item:
    def __init__(self, app_message: AppEntityPayloadItem) -> None:
        self._item_id: int = app_message.item_id
        self._quantity: int = app_message.quantity
        self._item_is_blueprint: bool = app_message.item_is_blueprint

    @property
    def item_id(self) -> int:
        return self._item_id

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def item_is_blueprint(self) -> bool:
        return self._item_is_blueprint


class TeamEvent:
    handlers = HandlerList()

    def __init__(self, app_message: AppMessage) -> None:
        self._player_id: int = app_message.broadcast.team_changed.player_id
        self._team_info = RustTeamInfo(app_message.broadcast.team_changed.team_info)

    @property
    def player_id(self) -> int:
        return self._player_id

    @property
    def team_info(self) -> RustTeamInfo:
        return self._team_info


class ChatEvent:
    handlers = HandlerList()

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


class EntityEvent:
    handlers = EntityHandlerList()

    def __init__(self, app_message: AppMessage, entity_type) -> None:
        self._type = int(entity_type)
        self._entity_id: int = app_message.broadcast.entity_changed.entity_id
        self._value: bool = app_message.broadcast.entity_changed.payload.value
        self._capacity: int = app_message.broadcast.entity_changed.payload.capacity
        self._has_protection: bool = (
            app_message.broadcast.entity_changed.payload.has_protection
        )
        self._protection_expiry: int = (
            app_message.broadcast.entity_changed.payload.protection_expiry
        )

        self._items: List[Item] = [
            Item(item) for item in app_message.broadcast.entity_changed.payload.items
        ]

    @property
    def type(self) -> int:
        return self._type

    @property
    def entity_id(self) -> int:
        return self._entity_id

    @property
    def value(self) -> bool:
        return self._value

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def has_protection(self) -> bool:
        return self._has_protection

    @property
    def protection_expiry(self) -> int:
        return self._protection_expiry

    @property
    def items(self) -> List[Item]:
        return self._items


class MarkerEvent:
    def __init__(self, marker, is_new) -> None:
        self._marker = marker
        self._is_new = is_new

    @property
    def marker(self) -> RustMarker:
        return self._marker

    @property
    def is_new(self) -> bool:
        return self._is_new


class ProtobufEvent:
    handlers = HandlerList()

    def __init__(self, byte_data) -> None:
        self._byte_data = byte_data

    @property
    def byte_data(self) -> bytes:
        return self._byte_data


class ClanInfoEvent:
    handlers = HandlerList()

    def __init__(self, clan_info: RustClanInfo) -> None:
        self._clan_info = clan_info

    @property
    def clan_info(self) -> RustClanInfo:
        return self._clan_info
