![Rust+.py](https://raw.githubusercontent.com/olijeffers0n/rustplus/master/icon.png)
<div align = "center">
	<img src = "https://static.pepy.tech/personalized-badge/rustplus?period=total&units=abbreviation&left_color=black&right_color=orange&left_text=Downloads">
	<img src = "https://img.shields.io/pypi/v/rustplus?label=PYPI%20Version">
	<img src = "https://img.shields.io/pypi/l/rustplus">
	<img src = "https://img.shields.io/github/stars/olijeffers0n/rustplus?label=GitHub%20Stars">
	<a href = "https://discord.gg/nQqJe8qvP8">
		<img src = "https://img.shields.io/discord/872406750639321088?label=Discord">
	</a>
</div>

A lot of code and ideas have come from the JavaScript version of a wrapper, so I will credit him now:
[RustPlus.js](https://github.com/liamcottle/rustplus.js)
I have used his Protocol Buffer file for this, as well as instructions on how to use his command line tool to get the information you need.

## Installation:
Install the package with:
```
pip install rustplus
```
It should also install all the dependencies, but if not you will have to install them yourself

## Usage:
```py
from  rustplus  import  RustSocket

rust_socket = RustSocket("IPADDRESS", "PORT", 64BITSTEAMID, PLAYERTOKEN)
#See below for more information on the above ^^

#Connects to the server's websocket
rust_socket.connect()

"""
For information on the following see below
"""
#Get mapMarkers:
markers = rust_socket.getMarkers()

#Get Server Info:
info = rust_socket.getInfo()

#Get Current time:
time = rust_socket.getTime()

#Getting Team info
team_info = rust_socket.getTeamInfo()

#Getting Team Chat:
team_chat = rust_socket.getTeamChat()

#Sending a Team Chat message:
status = rust_socket.sendTeamMessage("Yo! I sent this with Rust+.py")

#Get Camera Image:
camera_image = rust_socket.getCameraFrame("CAMID",FRAMENO)

#Get Map Image:
rust_map = rust_socket.getMap(addIcons = True, addEvents = True, addVendingMachines= True)

#Getting Map Data
rust_map_data = rust_socket.getRawMapData()

#Get Entity Information
entity_info = rust_socket.getEntityInfo(ENTITYID)

#Turning On/Off a Smart Switch
rust_socket.turnOffSmartSwitch(ENTITYID)
rust_socket.turnOnSmartSwitch(ENTITYID)

#Promoting a TeamMate to team leader
rust_socket.promoteToTeamLeader(SteamID)

#Getting the contents of a TC:
tc_contents = rust_socket.getTCStorageContents(ENTITYID, MERGESTACKS : bool)

#Getting Current Map Events
events = rust_socket.getCurrentEvents()

rust_socket.closeConnection()
```

# For information on all of the above methods, see the [Wiki](https://github.com/olijeffers0n/rustplus/wiki)

### Support:
If you need help, or you think that there is an issue feel free to open an issue. If you think you have made some improvements, open a PR! 

I have tried to explain this a well as possible, but if you should need further clarification, join me on my discord server: [here](https://discord.gg/nQqJe8qvP8)

I may add some of this functionality soon, depends on the interest :-)

Have Fun! 