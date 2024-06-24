# Events Overview

Socket Events are called whenever a specific action / event happens. There are currently 4 possible types of event that you could listen for:&#x20;

* Chat Event
* Entity Event
* Team Event
* Protobuf Event

These will be called by the socket when the respective events occur. Here are some example usages:

{% code title="listeners.py" %}

```python
from rustplus import EntityEvent, TeamEventPayload, ChatEventPayload


@rust_socket.entity_event(ENTITYID)
async def alarm(event: EntityEvent):
    value = "On" if event.value else "Off"
    print(f"{entity_type_to_string(event.type)} has been turned {value}")


@rust_socket.team_event
async def team(event: TeamEventPayload):
    print(f"The team leader's steamId is: {event.team_info.leader_steam_id}")


@rust_socket.chat_event
async def chat(event: ChatEventPayload):
    print(f"{event.message.name}: {event.message.message}")


@rust_socket.protobuf_received
async def proto(data: bytes):
    print(data)
```
{% endcode %}

### Entity Event

The `entity_event` decorator takes an extra parameter of the [entity id](../getting-started/getting-player-details/getting-entity-ids.md) that you are listening for changes to. The `EntityEvent` object holds information on the entity:

| Name                | Description                           |
| ------------------- | ------------------------------------- |
| `type`              | The type of entity, as an `int`       |
| `entity_id`         | The Entity Id                         |
| `value`             | The value of the entity, `boolean`    |
| `capacity`          | The capacity of the entity            |
| `has_protection`    | Whether the entity is protected by TC |
| `protection_expiry` | When the protection by TC will expire |
| `items`             | The items that the entity contains    |

### Team Event

This event is typically called when the team changes, e.g. a player leaves or joins. The `team_event` decorator will pass a `TeamEvent` object as a parameter with the following information:

| Name          | Description                                                                     |
| ------------- | ------------------------------------------------------------------------------- |
| `player_info` | The `player_id` of the changed information                                      |
| `team_info`   | The [`team info`](../api-methods/getting-team-info.md) on the team that changed |

### Chat Event

This event is called when a message is sent to the team chat. It will give you a `ChatEvent` object when called with this information:

| Name      | Description                                                      |
| --------- | ---------------------------------------------------------------- |
| `message` | The [message](../api-methods/getting-team-chat.md) that was sent |

### Protobuf Event

This event is called when protobuf is received over the websocket connection. This is for monitoring only. You are given the raw bytes of the message as a parameter.

### Removing

To remove any listener see:

{% content-ref url="../api-methods/removing-listeners.md" %}
[removing-listeners.md](../api-methods/removing-listeners.md)
{% endcontent-ref %}

