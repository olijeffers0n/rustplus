# Command Options

Command options are what you use to tell the [`RustSocket`](../getting-started/rustsocket/) what the general structure of your commands will be.
These define the prefix for the command, as well as any "overruling commands" which are commands that do not require a prefix. Usage:

```python
from rustplus import RustSocket, CommandOptions

options = CommandOptions(prefix="!")
```

