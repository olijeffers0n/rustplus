# Hanging The Socket

When using commands in a script, the script will terminate before you have a chance to listen to any commands. This is why you will need to hang the script.

```python
await rust_socket.hang()
```

This, however, is non-recoverable and will be stuck here until you force close the program.

