class RustMarker:

    def __init__(self, data) -> None:
        
        self.id = data.id
        self.type = data.type
        self.x = data.x
        self.y = data.y
        self.steamId = data.steamId
        self.rotation = data.rotation
        self.radius = data.radius
        self.colour1 = RustColour(data.color1)
        self.colour2 = RustColour(data.color2)
        self.alpha = data.alpha
        self.name = data.name
        self.sellOrders = [RustSellOrder(order) for order in data.sellOrders]

    def __str__(self) -> str:
        return "RustMarker[id={}, type={}, x={}, y={}, steamId={}, rotation={}, radius={}, colour1={}, colour2={}, alpha={}, name={}, sellOrders={}]".format(self.id, self.type, self.x, self.y, self.steamId, self.rotation, self.radius, self.colour1, self.colour2, self.alpha, self.name, len(self.sellOrders))


class RustColour:

    def __init__(self, data) -> None:

        self.x = data.x
        self.y = data.y
        self.z = data.z
        self.w = data.w

    def __str__(self) -> str:
        return "RustColour[x={}, y={}, z={}, w={}]".format(self.x, self.y, self.z, self.w)


class RustSellOrder:

    def __init__(self, data) -> None:

        self.itemId = data.itemId
        self.quantity = data.quantity
        self.currencyId = data.currencyId
        self.costPerItem = data.costPerItem
        self.itemIsBlueprint = data.itemIsBlueprint
        self.currencyIsBlueprint  = data.currencyIsBlueprint

    def __str__(self) -> str:
        return "RustSellOrder[itemId={}, quantity={}, currencyId={}, costPerItem={}, itemIsBlueprint={}, currencyIsBlueprint={}]".format(self.itemId, self.quantity, self.currencyId, self.costPerItem, self.itemIsBlueprint, self.currencyIsBlueprint)