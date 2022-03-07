from datetime import timedelta
from typing import List

from .rust_item import RustItem


class RustContents:
    def __init__(self, protection_time, has_protection, contents) -> None:
        self._protectionTime: timedelta = protection_time
        self._hasProtection: bool = has_protection
        self._contents: List[RustItem] = contents

    @property
    def protection_time(self) -> timedelta:
        return self._protectionTime

    @property
    def has_protection(self) -> bool:
        return self._hasProtection

    @property
    def contents(self) -> List[RustItem]:
        return self._contents

    def __setattr__(self, key, value):
        if hasattr(self, key):
            raise Exception("Cannot Re-Set Values")

    def __str__(self) -> str:
        return "RustContents[protectionTime={}, hasProtection={}, contents={}]".format(
            self._protectionTime, self._hasProtection, self.contents
        )
