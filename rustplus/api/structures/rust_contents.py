from datetime import timedelta
from typing import List

from .rust_item import RustItem


class RustContents:
    def __init__(self, protection_time, has_protection, contents) -> None:
        self._protection_time: timedelta = protection_time
        self._has_protection: bool = has_protection
        self._contents: List[RustItem] = contents

    @property
    def protection_time(self) -> timedelta:
        return self._protection_time

    @property
    def has_protection(self) -> bool:
        return self._has_protection

    @property
    def contents(self) -> List[RustItem]:
        return self._contents

    def __str__(self) -> str:
        return (
            "RustContents[protection_time={}, has_protection={}, contents={}]".format(
                self._protection_time, self._has_protection, self.contents
            )
        )
