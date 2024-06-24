from typing import List
from .serialization import Serializable
from ..remote import AppEntityInfo, AppEntityPayloadItem


class RustEntityInfoItem(Serializable):
    def __init__(self, data: AppEntityPayloadItem) -> None:
        self._item_id: int = data.item_id
        self._quantity: int = data.quantity
        self._item_is_blueprint: bool = data.item_is_blueprint

    @property
    def item_id(self) -> int:
        return self._item_id

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def item_is_blueprint(self) -> bool:
        return self._item_is_blueprint

    def __str__(self) -> str:
        return (
            "RustEntityInfoItem[item_id={}, quantity={}, item_is_blueprint={}]".format(
                self._item_id, self._quantity, self._item_is_blueprint
            )
        )


class RustEntityInfo(Serializable):
    def __init__(self, data: AppEntityInfo) -> None:
        self._type: int = data.type
        self._value: bool = data.payload.value
        self._items = [RustEntityInfoItem(item) for item in data.payload.items]
        self._capacity: int = data.payload.capacity
        self._has_protection: bool = data.payload.has_protection
        self._protection_expiry: int = data.payload.protection_expiry

    @property
    def type(self) -> int:
        return self._type

    @property
    def value(self) -> bool:
        return self._value

    @property
    def items(self) -> List[RustEntityInfoItem]:
        return self._items

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def has_protection(self) -> bool:
        return self._has_protection

    @property
    def protection_expiry(self) -> int:
        return self._protection_expiry

    def __str__(self) -> str:
        return "RustEntityInfo[type={}, value={}, items={}, capacity={}, has_protection={}, protection_expiry={}]".format(
            self._type,
            self._value,
            self._items,
            self._capacity,
            self._has_protection,
            self._protection_expiry,
        )
