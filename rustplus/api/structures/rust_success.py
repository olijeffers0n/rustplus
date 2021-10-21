class RustSuccess:

    def __init__(self, seq : int, success) -> None:

        self.seq = seq
        self.success = success

    def __str__(self) -> str:
        return "RustSuccess[seq={}, success={}]".format(self.seq, self.success)