class RustItem:
    def __init__(
        self, name: str, item_id: int, quantity: int, is_blueprint: bool
    ) -> None:
        self._name: str = name
        self._item_id: int = item_id
        self._quantity: int = quantity
        self._is_blueprint: bool = is_blueprint

    @property
    def name(self) -> str:
        return self._name

    @property
    def item_id(self) -> int:
        return self._item_id

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def is_blueprint(self) -> bool:
        return self._is_blueprint

    def __str__(self) -> str:
        return "RustItem[name={}, item_id={}, quantity={}, is_blueprint={}]".format(
            self._name, self._item_id, self._quantity, self._is_blueprint
        )
