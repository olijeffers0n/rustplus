from ..exceptions import PrefixNotDefinedError

class CommandOptions:

    def __init__(self, prefix : str = None) -> None:
        
        if prefix is None:
            raise PrefixNotDefinedError("Not Defined")

        self.prefix = prefix