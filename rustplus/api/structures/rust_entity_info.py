from typing import List


class RustEntityInfoItem:
    def __init__(self, data) -> None:
        self._itemId: int = data.itemId
        self._quantity: int = data.quantity
        self._itemIsBlueprint: bool = data.itemIsBlueprint

    @property
    def item_id(self) -> int:
        return self._itemId

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def item_is_blueprint(self) -> bool:
        return self._itemIsBlueprint

    def __setattr__(self, key, value):
        if hasattr(self, key):
            raise Exception("Cannot Re-Set Values")

    def __str__(self) -> str:
        return "RustEntityInfoItem[itemId={}, quantity={}, itemIsBlueprint={}]".format(
            self._itemId, self._quantity, self._itemIsBlueprint
        )


class RustEntityInfo:
    def __init__(self, data) -> None:
        self._type: int = data.type
        self._value: bool = data.payload.value
        self._items = [RustEntityInfoItem(item) for item in data.payload.items]
        self._capacity: int = data.payload.capacity
        self._hasProtection: bool = data.payload.hasProtection
        self._protectionExpiry: int = data.payload.protectionExpiry

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
        return self._hasProtection

    @property
    def protection_expiry(self) -> int:
        return self._protectionExpiry

    def __setattr__(self, key, value):
        if hasattr(self, key):
            raise Exception("Cannot Re-Set Values")

    def __str__(self) -> str:
        return "RustEntityInfo[type={}, value={}, items={}, capacity={}, hasProtection={}, protectionExpiry={}]".format(
            self._type,
            self._value,
            self._items,
            self._capacity,
            self._hasProtection,
            self._protectionExpiry,
        )
