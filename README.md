![Rust+.py](https://raw.githubusercontent.com/olijeffers0n/rustplus/master/icon.png)
<div align = "center">
	<img src = "https://static.pepy.tech/personalized-badge/rustplus?period=total&units=abbreviation&left_color=black&right_color=orange&left_text=Downloads">
	<img src = "https://img.shields.io/pypi/v/rustplus?label=PYPI%20Version">
	<img src = "https://img.shields.io/pypi/l/rustplus">
	<img src = "https://img.shields.io/github/stars/olijeffers0n/rustplus?label=GitHub%20Stars">
	<a href = "https://discord.gg/nQqJe8qvP8">
		<img src = "https://img.shields.io/discord/872406750639321088?label=Discord">
	</a>
    <div>
        <a href = "https://ko-fi.com/O5O3ALGLJ">
            <img src= "https://ko-fi.com/img/githubbutton_sm.svg" width="190">
        </a>
    </div>
</div>

A lot of code and ideas have come from the JavaScript version of a wrapper, so I will credit it now:
[RustPlus.js](https://github.com/liamcottle/rustplus.js)
I have used their Protocol Buffer file for generating the necessary requests so chuck some support their way

## Installation:
Install the package with:
```
pip install rustplus
```
It should also install all the dependencies, but if not you will have to install them yourself

## Usage:
```py
from rustplus import RustSocket, CommandOptions, Command, EntityEvent, TeamEvent, entity_type_to_string

#Registering the Command Options in order to listen for commands
options = CommandOptions(prefix="!")

rust_socket = RustSocket("IPADDRESS", "PORT", 64BITSTEAMID, PLAYERTOKEN, command_options=options)
#See below for more information on the above ^^

#Connects to the server's websocket
await rust_socket.connect()

"""
For information on the following see below
"""
#Get mapMarkers:
markers = await rust_socket.get_markers()

#Get Server Info:
info = await rust_socket.get_info()

#Get Current time:
time = await rust_socket.get_time()

#Getting Team info
team_info = await rust_socket.get_team_info()

#Getting Team Chat:
team_chat = await rust_socket.get_team_chat()

#Sending a Team Chat message:
await rust_socket.send_team_message("Yo! I sent this with Rust+.py")

#Get Map Image:
rust_map = await rust_socket.get_map(add_icons = True, add_events = True, add_vending_machines= True, override_images = {})

#Getting Map Data
rust_map_data = await rust_socket.get_raw_map_data()

#Get Entity Information
entity_info = await rust_socket.get_entity_info(ENTITYID)

#Turning On/Off a Smart Switch
await rust_socket.turn_off_smart_switch(ENTITYID)
await rust_socket.turn_on_smart_switch(ENTITYID)

#Promoting a TeamMate to team leader
await rust_socket.promote_to_team_leader(SteamID)

#Getting the contents of a TC:
tc_contents = await rust_socket.get_tc_storage_contents(ENTITYID, MERGESTACKS : bool)

#Getting Current Map Events
events = await rust_socket.get_current_events()

#Registering a command listener, which will listen for the command 'hi' with the prefix we defined earlier
@socket.command
async def hi(command : Command): 
  await rust_socket.send_team_message(f"Hi {command.sender_name}, This is an automated reply from RustPlus.py!")

@rust_socket.entity_event(ENTITYID)
async def alarm(event : EntityEvent):
  value = "On" if event.value else "Off"
  print(f"{entity_type_to_string(event.type)} has been turned {value}")

@rust_socket.team_event
async def team(event : TeamEvent):
  print(f"The team leader's steamId is: {event.teamInfo.leaderSteamId}")

#Used to just stop a script from ending. Use this if you are using commands or events in a script
await rust_socket.hang()

await rust_socket.close_connection()
```

# For information on all of the above methods, see the [Wiki](https://github.com/olijeffers0n/rustplus/wiki)

### Support:
If you need help, or you think that there is an issue feel free to open an issue. If you think you have made some improvements, open a PR! 

I have tried to explain this a well as possible, but if you should need further clarification, join me on my discord server: [here](https://discord.gg/nQqJe8qvP8)

GitHub ⭐'s are always welcome :)

Have Fun! 
