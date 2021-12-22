from typing import List
from datetime import timedelta
from .rust_item import RustItem

class RustContents:

    def __init__(self, protectionTime, hasProtection, contents) -> None:
        
        self.protectionTime : timedelta = protectionTime
        self.hasProtection : bool = hasProtection
        self.contents : List[RustItem] = contents

    def __str__(self) -> str:
        return "RustContents[protectionTime={}, hasProtection={}, contents={}]".format(self.protectionTime, self.hasProtection, self.contents)
