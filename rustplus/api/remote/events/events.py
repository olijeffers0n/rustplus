from typing import List

from ...structures import RustChatMessage
from ...structures.rust_team_info import RustTeamInfo
from ...structures.rust_marker import RustMarker
from .handler_list import HandlerList, EntityHandlerList


class Item:
    def __init__(self, app_message) -> None:
        self._item_id: int = app_message.itemId
        self._quantity: int = app_message.quantity
        self._item_is_blueprint: bool = app_message.itemIsBlueprint

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

    def __init__(self, app_message) -> None:
        self._player_id: int = app_message.broadcast.teamChanged.playerId
        self._team_info = RustTeamInfo(app_message.broadcast.teamChanged.teamInfo)

    @property
    def player_id(self) -> int:
        return self._player_id

    @property
    def team_info(self) -> RustTeamInfo:
        return self._team_info


class ChatEvent:

    handlers = HandlerList()

    def __init__(self, app_message) -> None:
        self._message = RustChatMessage(app_message.broadcast.teamMessage.message)

    @property
    def message(self) -> RustChatMessage:
        return self._message


class EntityEvent:

    handlers = EntityHandlerList()

    def __init__(self, app_message, entity_type) -> None:
        self._type = int(entity_type)
        self._entity_id: int = app_message.broadcast.entityChanged.entityId
        self._value: bool = app_message.broadcast.entityChanged.payload.value
        self._capacity: int = app_message.broadcast.entityChanged.payload.capacity
        self._has_protection: bool = (
            app_message.broadcast.entityChanged.payload.hasProtection
        )
        self._protection_expiry: int = (
            app_message.broadcast.entityChanged.payload.protectionExpiry
        )

        self._items: List[Item] = [
            Item(item) for item in app_message.broadcast.entityChanged.payload.items
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
