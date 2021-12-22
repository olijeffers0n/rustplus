class RustEntityInfo:

    def __init__(self, data) -> None:

        self.type : int = data.type
        self.value : bool = data.payload.value
        self.items = [RustEntityInfoItem(item) for item in data.payload.items]
        self.capacity : int = data.payload.capacity
        self.hasProtection : bool = data.payload.hasProtection
        self.protectionExpiry : int = data.payload.protectionExpiry 

    def __str__(self) -> str:
        return "RustEntityInfo[type={}, value={}, items={}, capacity={}, hasProtection={}, protectionExpiry={}]".format(self.type, self.value, self.items, self.capacity, self.hasProtection, self.protectionExpiry)


class RustEntityInfoItem:

    def __init__(self, data) -> None:
        
        self.itemId : int = data.itemId
        self.quantity : int = data.quantity
        self.itemIsBlueprint : bool = data.itemIsBlueprint

    def __str__(self) -> str:
        return "RustEntityInfoItem[itemId={}, quantity={}, itemIsBlueprint={}]".format(self.itemId, self.quantity, self.itemIsBlueprint)