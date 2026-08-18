---
description: How to get some functionality related to the Nexus system.
---

# Nexus

Currently, there is limited nexus functionality that is public access. You can access information via [getting-server-info.md](../api-methods/getting-server-info.md "mention") related to the current server. You can also access additional information via the `NexusInterface` .

* `get_all_nexus` - takes a public key (from FP) and a Realm and returns all Nexus on this server
* `get_nexus_info` - takes a nexus id and returns info about the nexus
* `get_nexus_map` - takes a nexus id and returns the map bytes

#### Example:

```python
from rustplus import Realm, NexusInterface
from PIL import Image
from io import BytesIO


interface = NexusInterface("https://gw.facepunch.com/nexus")

print(interface.get_all_nexus("PublicKey", Realm.Staging))

print(interface.get_nexus_info(2))

Image.open(BytesIO(interface.get_nexus_map(2))).show()
```
