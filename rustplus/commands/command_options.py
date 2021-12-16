class CommandOptions:

    def __init__(self, prefix : str = None) -> None:
        
        if prefix is None:
            raise Exception()

        self.prefix = prefix