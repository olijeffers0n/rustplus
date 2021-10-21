class RustItem:

    def __init__(self, name : str, itemId : int, quantity : int, isBlueprint : bool) -> None:
        
        self.name = name
        self.itemId = itemId
        self.quantity = quantity
        self.isBlueprint = isBlueprint

    def __str__(self) -> str:
        return "RustItem[name={}, itemId={}, quantity={}, isBlueprint={}]".format(self.name, self.itemId, self.quantity, self.isBlueprint)