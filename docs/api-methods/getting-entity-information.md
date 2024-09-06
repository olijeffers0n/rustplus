# Getting Entity Information

Calling `rust_socket.get_entity_info(entity_id: int)` will return a `RustEntityInfo` object with the following data:

```python
class RustEntityInfo with fields:

type: int
value: bool
items : RustEntityInfoItem
capacity: int
has_protection: bool
protection_expiry: int

class RustEntityInfoItem with fields:

item_id: int
quantity: int
item_is_blueprint: bool
```

The entity type is an integer value which corresponds to these values:

```
Switch = 1
Alarm = 2
StorageMonitor = 3
```

## Setting Entity Information

Calling `rust_socket.set_entity_value(entity_id: int, value: bool)` will set the value of the entity with the given ID to the given value.

