# Rate Limiting

The server uses a '[Token Bucket](https://en.wikipedia.org/wiki/Token\_bucket)' approach meaning that you should be careful how many requests you send, however if you are sensible, this should be a non-issue...

You get: 50 tokens max per IP address with 15 replenished per second 25 tokens max per PlayerID with 3 replenished per second

And these are the costs:

```
get_map = 5 or 6 (depending on what you add to the map)
get_time = 1
get_info = 1
get_markers = 1
send_team_chat = 2
get_team_info = 1
turn_on_switch = 1
turn_off_switch = 1
get_entitiy_info = 1
promote_to_team_leader = 1
get_tc_storage_contents = 1
get_current_events = 1

Registering Entity Events = 1
```

RustPlus.py now handles ratelimiting automatically. It can either raise exceptions when you are going to exceed the limit or it can wait and send it later when you have enough tokens. Change this in the `RustSocket` constructor (`raise_ratelimit_exception`). This defaults to `True`, so set it to false if you want the socket to wait until you can afford the operations.

