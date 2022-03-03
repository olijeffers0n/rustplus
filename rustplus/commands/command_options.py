from typing import List

from ..exceptions import PrefixNotDefinedError


class CommandOptions:
    def __init__(
        self, prefix: str = None, overruling_commands: List[str] = None
    ) -> None:

        if prefix is None:
            raise PrefixNotDefinedError("No prefix")

        if overruling_commands is None:
            overruling_commands = []

        self.prefix = prefix
        self.overruling_commands = overruling_commands
