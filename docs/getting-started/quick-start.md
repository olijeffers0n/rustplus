# Quick Start

In order to access the API, you must first install the package using pip:

```shell
pip install rustplus
```

You must then get your Personal details using the web tool, as shown here:

{% content-ref url="getting-player-details/" %}
[getting-player-details](getting-player-details/)
{% endcontent-ref %}

{% code title="main.py" %}
```python
import asyncio
from rustplus import RustSocket, ServerDetails

async def main():
    server_details = ServerDetails("IP", "PORT", STEAMID, PLAYERTOKEN)
    socket = RustSocket(server_details)
    await socket.connect()

    print(f"It is {(await socket.get_time()).time}")

    await socket.disconnect()

asyncio.run(main())
```
{% endcode %}

This will run, and print the time on the Rust Server.

API methods will return an instance of `RustError` if they are not successful. This is to allow for better error handling, and reconnecting to the server. You can detect these by:

{% code title="main.py" %}
```python
time = await socket.get_time()
if isinstance(time, RustError):
    print(f"Error Occurred, Reason: {time.reason}")
```
