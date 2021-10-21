class RustEntityInfo:

    def __init__(self, data) -> None:

        self.type = data.type
        self.value = data.payload.value
        self.items = [RustEntityInfoItem(item) for item in data.payload.items]
        self.capacity = data.payload.capacity
        self.hasProtection = data.payload.hasProtection
        self.protectionExpiry = data.payload.protectionExpiry 

    def __str__(self) -> str:
        return "RustEntityInfo[type={}, value={}, items={}, capacity={}, hasProtection={}, protectionExpiry={}]".format(self.type, self.value, self.items, self.capacity, self.hasProtection, self.protectionExpiry)


class RustEntityInfoItem:

    def __init__(self, data) -> None:
        
        self.itemId = data.itemId
        self.quantity = data.quantity
        self.itemIsBlueprint = data.itemIsBlueprint

    def __str__(self) -> str:
        return "RustEntityInfoItem[itemId={}, quantity={}, itemIsBlueprint={}]".format(self.itemId, self.quantity, self.itemIsBlueprint)