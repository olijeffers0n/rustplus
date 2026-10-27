# RustSocket

The `RustSocket` is where everything happens in Rust+.py. Constructing one is super easy. There is only 1 required argument. But that doesn't mean that's all!

```python
from rustplus import RustSocket

socket = RustSocket(
                server_details: ServerDetails,
                ratelimiter: RateLimiter | None = None,
                command_options: CommandOptions | None = None,
                debug: bool = False
        )
```

<table><thead><tr><th width="308.9185519409846">Name</th><th width="176.31844290093184">Type</th><th>What it is </th></tr></thead><tbody><tr><td><code>server_details</code></td><td><code>ServerDetails</code></td><td>The details for the socket to connect to</td></tr><tr><td><code>command_options</code></td><td><code>CommandOptions</code></td><td>The Command Options</td></tr><tr><td><code>ratelimiter</code></td><td><code>RateLimiter</code></td><td>A shared <code>RateLimiter</code> to be used across sockets.</td></tr><tr><td><code>debug</code></td><td><code>bool</code></td><td>Whether to output debug messages</td></tr></tbody></table>



