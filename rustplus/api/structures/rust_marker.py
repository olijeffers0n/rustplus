class RustMarker:

    def __init__(self, data) -> None:
        
        self.id : int = data.id
        self.type : int = data.type
        self.x : float = data.x
        self.y : float = data.y
        self.steamId : int = data.steamId
        self.rotation : float = data.rotation
        self.radius : float = data.radius
        self.colour1 = RustColour(data.color1)
        self.colour2 = RustColour(data.color2)
        self.alpha : float = data.alpha
        self.name : str = data.name
        self.sellOrders = [RustSellOrder(order) for order in data.sellOrders]

    def __str__(self) -> str:
        return "RustMarker[id={}, type={}, x={}, y={}, steamId={}, rotation={}, radius={}, colour1={}, colour2={}, alpha={}, name={}, sellOrders={}]".format(self.id, self.type, self.x, self.y, self.steamId, self.rotation, self.radius, self.colour1, self.colour2, self.alpha, self.name, self.sellOrders)


class RustColour:

    def __init__(self, data) -> None:

        self.x : float = data.x
        self.y : float = data.y
        self.z : float = data.z
        self.w : float = data.w

    def __str__(self) -> str:
        return "RustColour[x={}, y={}, z={}, w={}]".format(self.x, self.y, self.z, self.w)


class RustSellOrder:

    def __init__(self, data) -> None:

        self.itemId : int = data.itemId
        self.quantity : int = data.quantity
        self.currencyId : int = data.currencyId
        self.costPerItem : int = data.costPerItem
        self.itemIsBlueprint : bool = data.itemIsBlueprint
        self.currencyIsBlueprint : bool = data.currencyIsBlueprint

    def __str__(self) -> str:
        return "RustSellOrder[itemId={}, quantity={}, currencyId={}, costPerItem={}, itemIsBlueprint={}, currencyIsBlueprint={}]".format(self.itemId, self.quantity, self.currencyId, self.costPerItem, self.itemIsBlueprint, self.currencyIsBlueprint)