# Getting Server Info

Calling `rust_socket.get_info()` will return a `RustInfo` object with the following data:

```python
class RustInfo with fields:

url: str
name: str
map: str
size: int
players: int
max_players: int
queued_players: int 
seed: int
```

