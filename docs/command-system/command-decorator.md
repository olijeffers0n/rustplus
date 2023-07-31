# Command Decorator

The command decorator is used to mark a coroutine as a command listener. Usage:

```python
@rust_socket.command
async def hi(command: Command):
    print("Command Ran!")
```

The fact that the coroutine's name is `hi` means that the command will be `<prefix>hi` .

You also get access to this `Command` object which has a slew of useful information about the how the command was called.

| Field            | Value                                                                                                                                         |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `sender_name`    | The name of the person that called the command, e.g. `olijeffers0n`                                                                           |
| `sender_steamid` | The steamID of the person that called the command                                                                                             |
| `time`           | The time that the command was called, as a `CommandTime` object. This wraps a `datetime` object, and the raw UNIX Epoch time                  |
| `command`        | The name of the command that was called, e.g. `hi`                                                                                            |
| `args`           | A list of strings that was passed as arguments to the command. E.g. - `!hi one two three` would result in args being `["one", "two, "three"]` |

This decorator returns a [`RegisteredListener`](../api-methods/removing-listeners.md#registered-listeners) instance

### Aliases

You don't want to have to register 100's of commands for every permutation of phrasing, so why should you!

```python
@rust_socket.command(aliases=["hello", "hey"])
async def hi(command: Command):
    print("Command Ran!")
```

This is a simple example of how you could incorporate different function names into one command, but sometimes we need more than that!

```python
@rust_socket.command(alais_func=lambda x: x.lower() == "test")
async def pair(command: Command):
    print("Command Ran!")
```

This will allow you to check ANY string as it is passed in and perform checking on it. You just have to provide a callable, so a lambda or function reference will work! It will provide the current command as an argument and you can perform any logic you need!

