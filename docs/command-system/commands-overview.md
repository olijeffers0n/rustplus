# Commands Overview

Commands allow the triggering of custom coroutines when a specific keyword is sent in the **team** chat. Basic Usage:

{% code title="main.py" %}
```python
from rustplus import RustSocket, CommandOptions, Command

options = CommandOptions(prefix="!") # Use whatever prefix you want here
rust_socket = RustSocket("IP", "PORT", STEAMID, PLAYERTOKEN, command_options=options)

@rust_socket.command
async def hi(command : Command): 
    await socket.send_team_message(f"Hi, {command.sender_name}")
```
{% endcode %}

