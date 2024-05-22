# Getting Team Info

Calling `rust_socket.get_team_info()` returns a `RustTeamInfo` object with the following data:

```python
class RustTeamInfo with fields:

leader_steam_id: int
members : List[RustTeamMember]
map_notes : List[RustTeamNote]
leader_map_notes : List[RustTeamNote]

class RustTeamMember with fields:

steam_id: int
name: str
x: float
y: float
is_online: bool
spawn_time: int
is_alive: bool
death_time: int

class RustTeamNote with fields:

type: int
x: float
y: float
icon: int
colour_index: int
label: string
```

So, to get the name of the first member in the team you can do:

```python
info = await rust_socket.get_team_info()
print(info.members[0].name)
```

