from typing import List

from rustplus.identification.handler_list import EntityHandlerList
from ..remote.rustplus_proto import AppEntityPayloadItem, AppEntityChanged


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


class EntityEventPayload:
    HANDLER_LIST = EntityHandlerList()

    def __init__(self, entity_changed: AppEntityChanged, entity_type) -> None:
        self._type = int(entity_type)  # TODO CHECK HOW I HANDLE THIS
        self._entity_id: int = entity_changed.entity_id
        self._value: bool = entity_changed.payload.value
        self._capacity: int = entity_changed.payload.capacity
        self._has_protection: bool = entity_changed.payload.has_protection
        self._protection_expiry: int = entity_changed.payload.protection_expiry

        self._items: List[Item] = [Item(item) for item in entity_changed.payload.items]

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
