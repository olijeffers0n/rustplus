class RustContents:

    def __init__(self, protectionTime, hasProtection, contents) -> None:
        
        self.protectionTime = protectionTime
        self.hasProtection = hasProtection
        self.contents = contents

    def __str__(self) -> str:
        return "RustContents[protectionTime={}, hasProtection={}, contents={}]".format(self.protectionTime, self.hasProtection, self.contents)
