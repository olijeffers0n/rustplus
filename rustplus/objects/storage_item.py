class Storage_Item:
    def __init__(self, name : str, itemId : int, quantity : int, isBlueprint : bool) -> None:
        self.name = name
        self.itemId = itemId
        self.quantity = quantity
        self.isBlueprint = isBlueprint

    def __repr__(self) -> str:
        return "Storage Item(name = {} | itemId = {} | quantity = {} | isBlueprint = {})".format(self.name, self.itemId, self.quantity, self.isBlueprint)