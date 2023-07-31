# Quick Start

In order to access the API, you must first install the package using pip:

```shell
pip install rustplus
```

You must then get your Personal details using the RustCli, as shown here:

{% content-ref url="getting-player-details/" %}
[getting-player-details](getting-player-details/)
{% endcontent-ref %}

{% code title="main.py" %}
```python
import asyncio
from rustplus import RustSocket

async def main():
    socket = RustSocket("IP", "PORT", STEAMID, PLAYERTOKEN)
    await socket.connect()

    print(f"It is {(await socket.get_time()).time}")

    await socket.disconnect()

asyncio.run(main())
```
{% endcode %}

This will run, and print the time on the Rust Server

