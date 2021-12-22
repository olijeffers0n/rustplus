class RustItem:

    def __init__(self, name : str, itemId : int, quantity : int, isBlueprint : bool) -> None:
        
        self.name : str = name
        self.itemId : int = itemId
        self.quantity : int = quantity
        self.isBlueprint : bool = isBlueprint

    def __str__(self) -> str:
        return "RustItem[name={}, itemId={}, quantity={}, isBlueprint={}]".format(self.name, self.itemId, self.quantity, self.isBlueprint)