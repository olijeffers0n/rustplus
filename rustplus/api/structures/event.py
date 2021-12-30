from typing import List

class EntityEvent:

    def __init__(self, app_message, type) -> None:
        
        self.type = type
        self.entityId : int = app_message.broadcast.entityChanged.entityId 
        self.value : bool = app_message.broadcast.entityChanged.payload.value
        self.capacity : int = app_message.broadcast.entityChanged.payload.capacity
        self.hasProtection : bool = app_message.broadcast.entityChanged.payload.hasProtection
        self.protectionExpiry : bool = app_message.broadcast.entityChanged.payload.protectionExpiry

        self.items : List[Item] = [Item(item) for item in app_message.broadcast.entityChanged.payload.items]

class Item:

    def __init__(self, app_message) -> None:

        self.itemId : int = app_message.itemId
        self.quantity : int = app_message.quantity
        self.itemIsBlueprint : bool = app_message.itemIsBlueprint
