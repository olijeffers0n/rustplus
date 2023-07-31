# Getting Map Markers

Calling `rust_socket.get_markers()` returns a `List[RustMarker]` with the following data:

```python
class RustMarker with fields:

id: int
type: int
x: float
y: float
steam_id: int
rotation: float
radius: float
colour1 : RustColour
colour2 : RustColour
alpha: float
name: str
sell_orders : List[RustSellOrder]

class RustColour with fields:

x: float
y: float
z: float
w: float

class RustSellOrder with fields:

item_id: int
quantity: int
currency_id: int
cost_per_item: int
item_is_blueprint: bool
currency_is_blueprint: bool
amount_in_stock: int
```

#### These are the types of the RustMarker

```
Types:
	Player = 1
	Explosion = 2
	VendingMachine = 3
	CH47 = 4
	CargoShip = 5
	Crate = 6
	GenericRadius = 7
	PatrolHelicopter = 8
```

