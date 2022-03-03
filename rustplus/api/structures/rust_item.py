class RustItem:
    def __init__(
        self, name: str, item_id: int, quantity: int, is_blueprint: bool
    ) -> None:
        self.name: str = name
        self.itemId: int = item_id
        self.quantity: int = quantity
        self.isBlueprint: bool = is_blueprint

    def __str__(self) -> str:
        return "RustItem[name={}, itemId={}, quantity={}, isBlueprint={}]".format(
            self.name, self.itemId, self.quantity, self.isBlueprint
        )
