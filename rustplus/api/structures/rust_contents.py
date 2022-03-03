from datetime import timedelta
from typing import List

from .rust_item import RustItem


class RustContents:
    def __init__(self, protection_time, has_protection, contents) -> None:
        self.protectionTime: timedelta = protection_time
        self.hasProtection: bool = has_protection
        self.contents: List[RustItem] = contents

    def __str__(self) -> str:
        return "RustContents[protectionTime={}, hasProtection={}, contents={}]".format(
            self.protectionTime, self.hasProtection, self.contents
        )
