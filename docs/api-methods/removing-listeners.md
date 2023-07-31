# Removing Listeners

### Registered Listeners

A registered listener is a wrapper object around the coroutine itself that will allow the listener to be removed later on. Should you need the coroutine back, call `RegisteredListener.get_coro()`.

### Removing The listener

Removing a listener is as simple as calling `RustSocket.remove_listener(RegisteredListener)` and will return a boolean value. True if a listener was removed and false otherwise

