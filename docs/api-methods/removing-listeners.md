# Removing Listeners

### Registered Listeners

A registered listener is a wrapper object around the coroutine itself that will allow the listener to be removed later 
on. Should you need the coroutine back, call `RegisteredListener.get_coro()`.

### Removing The listener

Removing a listener is as simple as using an Event's HandlerList. This is one example:

```python
@EntityEvent(server_details, 25743493)
async def on_entity_event(payload: EntityEventPayload):
    await rust_socket.set_entity_value(payload.entity_id, not payload.value)
    
    
EntityEventPayload.HANDLER_LIST.unregister(on_entity_event, server_details)

# You can also unregister all listeners for a specific event
EntityEventPayload.HANDLER_LIST.unregister_all()
```
