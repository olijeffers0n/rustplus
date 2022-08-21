from typing import List


class RustColour:
    def __init__(self, data) -> None:
        self._x: float = data.x
        self._y: float = data.y
        self._z: float = data.z
        self._w: float = data.w

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @property
    def z(self) -> float:
        return self._z

    @property
    def w(self) -> float:
        return self._w

    def __str__(self) -> str:
        return "RustColour[x={}, y={}, z={}, w={}]".format(
            self._x, self._y, self._z, self._w
        )


class RustSellOrder:
    def __init__(self, data) -> None:
        self._item_id: int = data.itemId
        self._quantity: int = data.quantity
        self._currency_id: int = data.currencyId
        self._cost_per_item: int = data.costPerItem
        self._item_is_blueprint: bool = data.itemIsBlueprint
        self._currency_is_blueprint: bool = data.currencyIsBlueprint
        self._amount_in_stock: int = data.amountInStock

    @property
    def item_id(self) -> int:
        return self._item_id

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def currency_id(self) -> int:
        return self._currency_id

    @property
    def cost_per_item(self) -> int:
        return self._cost_per_item

    @property
    def item_is_blueprint(self) -> bool:
        return self._item_is_blueprint

    @property
    def currency_is_blueprint(self) -> bool:
        return self._currency_is_blueprint

    @property
    def amount_in_stock(self) -> int:
        return self._amount_in_stock

    def __str__(self) -> str:
        return (
            "RustSellOrder[item_id={}, quantity={}, currency_id={}, cost_per_item={}, item_is_blueprint={}, "
            "currency_is_blueprint={}]".format(
                self._item_id,
                self._quantity,
                self._currency_id,
                self._cost_per_item,
                self._item_is_blueprint,
                self._currency_is_blueprint,
            )
        )


class RustMarker:

    PlayerMarker = 1
    ExplosionMarker = 2
    VendingMachineMarker = 3
    ChinookMarker = 4
    CargoShipMarker = 5
    CrateMarker = 6
    RadiusMarker = 7
    PatrolHelicopterMarker = 8

    def __init__(self, data) -> None:
        self._id: int = data.id
        self._type: int = data.type
        self._x: float = data.x
        self._y: float = data.y
        self._steam_id: int = data.steamId
        self._rotation: float = data.rotation
        self._radius: float = data.radius
        self._colour1 = RustColour(data.color1)
        self._colour2 = RustColour(data.color2)
        self._alpha: float = data.alpha
        self._name: str = data.name
        self._out_of_stock: bool = data.outOfStock
        self._sell_orders = [RustSellOrder(order) for order in data.sellOrders]

    @property
    def id(self) -> int:
        return self._id

    @property
    def type(self) -> int:
        return self._type

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @property
    def steam_id(self) -> int:
        return self._steam_id

    @property
    def rotation(self) -> float:
        return self._rotation

    @property
    def radius(self) -> float:
        return self._radius

    @property
    def colour1(self) -> RustColour:
        return self._colour1

    @property
    def colour2(self) -> RustColour:
        return self._colour2

    @property
    def alpha(self) -> float:
        return self._alpha

    @property
    def name(self) -> str:
        return self._name

    @property
    def sell_orders(self) -> List[RustSellOrder]:
        return self._sell_orders

    @property
    def out_of_stock(self) -> bool:
        return self._out_of_stock

    def __eq__(self, other):
        if isinstance(other, RustMarker):
            return self.id == other.id
        return False

    def __str__(self) -> str:
        return (
            "RustMarker[id={}, type={}, x={}, y={}, steam_id={}, rotation={}, radius={}, colour1={}, colour2={}, "
            "alpha={}, name={}, sell_orders={}, out_of_stock={}]".format(
                self._id,
                self._type,
                self._x,
                self._y,
                self._steam_id,
                self._rotation,
                self._radius,
                self._colour1,
                self._colour2,
                self._alpha,
                self._name,
                self._sell_orders,
                self._out_of_stock,
            )
        )
