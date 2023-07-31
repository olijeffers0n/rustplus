# Command Options

Command options are what you use to tell the [`RustSocket`](../getting-started/rustsocket/) what the general structure of your commands will be. These define the prefix for the command, as well as any "overruling commands" which are commands that do not require a prefix. Usage:

```python
from rustplus import RustSocket

options = CommandOptions(prefix="!", overruling_commands = ["time"])

# Prefix is a string, and the overruling_commands are a list of strings which would be the name of the coroutines
```

You can then just pass these into the RustSocket constructor using the `overruling_commands` kwarg.

