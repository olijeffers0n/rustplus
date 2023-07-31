# RustSocket

The `RustSocket` is where everything happens in Rust+.py. Constructing one is super easy. There are only 4 required arguments, the Ip, Port, SteamId and Token. But that doesn't mean that's all!

```python
from rustplus import RustSocket

socket = RustSocket(ip, port, steam_id, player_token, 
                    command_options, raise_ratelimit_exception, ratelimit_limit, 
                    ratelimit_refill, use_proxy)
```

<table><thead><tr><th width="308.9185519409846">Name</th><th width="176.31844290093184">Type</th><th>What it is </th></tr></thead><tbody><tr><td><code>ip</code></td><td><code>str</code></td><td>The Ip of the Server</td></tr><tr><td><code>port</code></td><td><code>str</code></td><td>The port of the server</td></tr><tr><td><code>steam_id</code></td><td><code>int</code></td><td>Your SteamID</td></tr><tr><td><code>player_token</code></td><td><code>int</code></td><td>Your player token</td></tr><tr><td><code>command_options</code></td><td><code>CommandOptions</code></td><td>The Command Options</td></tr><tr><td><code>raise_ratelimit_exception</code></td><td><code>bool</code></td><td>Whether to raise an exception if you run into the ratelimit. Set to false to automatically wait until you can afford the request</td></tr><tr><td><code>ratelimit_limit</code></td><td><code>int</code></td><td>The upper limit of the <code>TokenBucket</code></td></tr><tr><td><code>ratelimit_refill</code></td><td><code>int</code></td><td>The refill rate of the <code>TokenBucket</code></td></tr><tr><td><code>use_proxy</code></td><td><code>bool</code></td><td>Whether to use the Facepunch Proxy. <code>False</code> by default</td></tr></tbody></table>



