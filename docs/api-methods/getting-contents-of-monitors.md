# Getting Contents of Monitors

Calling `rust_socket.get_contents(eid: int, combine_stacks: bool)` returns a `RustContents` object:



```python
class RustContents with fields:

protection_time: timedelta
has_protection: bool
contents : List[RustItem]
        
class RustItem with fields:

name: str
item_id: int
quantity: int
is_blueprint: bool
```

