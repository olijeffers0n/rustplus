# Commands Overview

Commands allow the triggering of custom coroutines when a specific keyword is sent in the **team** chat. Basic Usage:

{% code title="main.py" %}
```python
from rustplus import RustSocket, CommandOptions, Command, ServerDetails, Command, ChatCommand

options = CommandOptions(prefix="!") # Use whatever prefix you want here
server_details = ServerDetails("IP", "PORT", STEAMID, PLAYERTOKEN)
socket = RustSocket(server_details)

@Command(server_details)
async def hi(command : ChatCommand): 
    await socket.send_team_message(f"Hi, {command.sender_name}")
```
{% endcode %}

