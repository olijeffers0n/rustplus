class RustItem:
    def __init__(
        self, name: str, item_id: int, quantity: int, is_blueprint: bool
    ) -> None:
        self._name: str = name
        self._itemId: int = item_id
        self._quantity: int = quantity
        self._isBlueprint: bool = is_blueprint

    @property
    def name(self) -> str:
        return self._name

    @property
    def item_id(self) -> int:
        return self._itemId

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def is_blueprint(self) -> bool:
        return self._isBlueprint

    def __setattr__(self, key, value):
        if hasattr(self, key):
            raise Exception("Cannot Re-Set Values")

    def __str__(self) -> str:
        return "RustItem[name={}, itemId={}, quantity={}, isBlueprint={}]".format(
            self._name, self._itemId, self._quantity, self._isBlueprint
        )
