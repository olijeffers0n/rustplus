# Getting the Map

### Getting the Image

Calling `rust_socket.get_map(add_icons: bool, add_events: bool, add_vending_machines: bool, override_images: dict)` will return a `PIL.Image` with the respective additions.

### Getting the Map Data

Calling `rust_socket.get_raw_map_data()` will return a `RustMap` object with the following data:

```python
class RustMap with fields:

width: int
height: int
jpg_image: bytes
margin: int
monuments : List[RustMonument]
background: str

class RustMonument with fields:

token: str
x: float
y: float
```

