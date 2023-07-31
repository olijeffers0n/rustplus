# Getting Team Chat

Calling `rust_socket.get_team_chat()` will return a `List[RustChatMessage]` objects with fields:

```python
class RustChatMessage with fields:

steam_id: int
name: str
message: str
colour: str
time: int
```

