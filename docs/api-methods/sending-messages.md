# Sending Messages

Calling `rust_socket.send_team_message(message: str)` will send the message to the team chat as the player who you are logged in as in the [`RustSocket`](../getting-started/rustsocket/) . For example:

```python
await rust_socket.send_team_message("Hi! This was sent with Rust+.py")
```

