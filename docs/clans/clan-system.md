# Clan System

Clans can be accessed and controlled via the Rust+ API.

### Getting Clan Information

Retrieve information about the clan that the authenticated player belongs to.

```python
from rustplus import RustSocket

clan = await socket.get_clan_info()

print(clan.clan_name)
print(clan.max_members)
print(clan.motd)
```

The returned `RustClanInfo` object contains information such as:

* Clan name
* Clan tag
* Message of the Day
* Leader information
* Member list
* Other metadata exposed by the Rust+ API

Example:

```python
clan = await socket.get_clan_info()

print(f"{clan.clan_id} - {clan.name}")
print(f"Members: {len(clan.members)}")

for member in clan.members:
    print(member.steam_id)
```

***

## Reading Clan Chat

Retrieve the recent clan chat history.

```python
messages = await socket.get_clan_chat()

for message in messages:
    print(f"[{message.timestamp}] {message.name}: {message.message}")
```

`get_clan_chat()` returns a list of `RustClanMessage` objects.

Each message contains information such as:

* Sender name
* Steam ID
* Message text
* Timestamp

***

## Sending a Clan Message

Send a message to the clan chat.

```python
await socket.send_clan_message(
    "Raid starts in 30 minutes."
)
```

Another example:

```python
await socket.send_clan_message(
    "Boxes have been organised in the main base."
)
```

This method sends the message asynchronously and does not return a response from the server.

***

## Updating the Clan MOTD

Update the clan's Message of the Day.

```python
await socket.set_clan_motd(
    "Welcome! Raid tonight at 20:00 UTC."
)
```

Only players with sufficient clan permissions can change the MOTD.

***

## Error Handling

Like other request methods in RustPlus.py, clan requests may return a `RustError`.

```python
from rustplus import RustError

result = await socket.get_clan_info()

if isinstance(result, RustError):
    print(result.error)
else:
    print(result.clan_name)
```

***

## Complete Example

```python
from rustplus import RustSocket, RustError

clan = await rust_socket.get_clan_info()

if isinstance(clan, RustError):
    print(f"Failed to retrieve clan information: {clan.error}")
else:
    print(f"Clan: [{clan.clan_id}] {clan.clan_name}")
    print(f"MOTD: {clan.motd}")

messages = await rust_socket.get_clan_chat()

if not isinstance(messages, RustError):
    print("\nRecent clan chat:")

    for message in messages[-5:]:
        print(f"{message.name}: {message.message}")

await rust_socket.send_clan_message("Hello from RustPlus.py!")
```

I'd recommend documenting the public properties rather than the private backing fields (`_clan_id`, `_steam_id`, etc.), since those are what users interact with. Here's documentation you could put in your API docs.

***

## `RustClanInfo`

Represents the current clan and all of its metadata.

| Property            | Type                   | Description                                                                                          |
| ------------------- | ---------------------- | ---------------------------------------------------------------------------------------------------- |
| `clan_id`           | `int`                  | Unique identifier of the clan.                                                                       |
| `clan_name`         | `str`                  | The display name of the clan.                                                                        |
| `clan_time_created` | `int`                  | Unix timestamp indicating when the clan was created.                                                 |
| `creator`           | `int`                  | 64-bit Steam ID of the player who created the clan.                                                  |
| `motd`              | `str`                  | The clan's current Message of the Day.                                                               |
| `motd_time_set`     | `int`                  | Unix timestamp of when the MOTD was last updated.                                                    |
| `motd_author`       | `int`                  | 64-bit Steam ID of the player who last updated the MOTD.                                             |
| `logo`              | `bytes`                | Raw image data for the clan logo. Can be written directly to a file or loaded into an image library. |
| `colour`            | `int`                  | Integer representing the clan's chosen colour.                                                       |
| `roles`             | `List[RustClanRole]`   | List of all roles defined within the clan.                                                           |
| `members`           | `List[RustClanMember]` | List of every member currently in the clan.                                                          |
| `invites`           | `List[RustClanInvite]` | List of all outstanding clan invitations.                                                            |
| `max_members`       | `int`                  | Maximum number of members the clan can contain.                                                      |

#### Example

```python
clan = await socket.get_clan_info()

print(clan.clan_name)
print(clan.motd)
print(len(clan.members))
```

***

## `RustClanRole`

Represents a role within the clan and its permissions.

| Property               | Type   | Description                                                                        |
| ---------------------- | ------ | ---------------------------------------------------------------------------------- |
| `role_id`              | `int`  | Unique identifier of the role.                                                     |
| `rank`                 | `int`  | Numerical rank of the role. Higher ranking roles generally have greater authority. |
| `name`                 | `str`  | Display name of the role.                                                          |
| `can_set_motd`         | `bool` | Whether members with this role can change the clan MOTD.                           |
| `can_set_logo`         | `bool` | Whether members with this role can change the clan logo.                           |
| `can_invite`           | `bool` | Whether members with this role can invite new players.                             |
| `can_kick`             | `bool` | Whether members with this role can remove members from the clan.                   |
| `can_promote`          | `bool` | Whether members with this role can promote other members.                          |
| `can_demote`           | `bool` | Whether members with this role can demote other members.                           |
| `can_set_player_notes` | `bool` | Whether members with this role can edit notes attached to clan members.            |
| `can_access_logs`      | `bool` | Whether members with this role can access clan logs.                               |

#### Example

```python
for role in clan.roles:
    print(role.name)

    if role.can_invite:
        print("Can invite players")
```

***

## `RustClanMember`

Represents a member of the clan.

| Property      | Type   | Description                                                                                                 |
| ------------- | ------ | ----------------------------------------------------------------------------------------------------------- |
| `steam_id`    | `int`  | 64-bit Steam ID of the player.                                                                              |
| `role_id`     | `int`  | Identifier of the member's assigned role. Match this against `RustClanRole.role_id` to obtain role details. |
| `joined_time` | `int`  | Unix timestamp indicating when the player joined the clan.                                                  |
| `last_seen`   | `int`  | Unix timestamp of when the player was last seen online.                                                     |
| `notes`       | `str`  | Notes attached to the player by clan members. May be empty.                                                 |
| `online`      | `bool` | Whether the player is currently online.                                                                     |

#### Example

```python
for member in clan.members:
    status = "Online" if member.online else "Offline"

    print(f"{member.steam_id} - {status}")
```

To retrieve the member's role:

```python
role = next(
    role for role in clan.roles
    if role.role_id == member.role_id
)

print(role.name)
```

***

## `RustClanInvite`

Represents a pending invitation to join the clan.

| Property       | Type  | Description                                             |
| -------------- | ----- | ------------------------------------------------------- |
| `steam_id`     | `int` | 64-bit Steam ID of the invited player.                  |
| `recruiter`    | `int` | 64-bit Steam ID of the player who sent the invitation.  |
| `invited_time` | `int` | Unix timestamp indicating when the invitation was sent. |

#### Example

```python
for invite in clan.invites:
    print(invite.steam_id)
```

***

### Working with Unix Timestamps

Several properties (`joined_time`, `last_seen`, `clan_time_created`, `motd_time_set`, and `invited_time`) are returned as Unix timestamps.

```python
from datetime import datetime

created = datetime.fromtimestamp(clan.clan_time_created)

print(created.strftime("%d %B %Y"))
```

This gives users a complete reference for every public field while also demonstrating the intended way to work with the objects.
