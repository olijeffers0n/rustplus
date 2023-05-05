import asyncio
import contextlib
from typing import Any, Union


class YieldingEvent(asyncio.Event):
    def __init__(self) -> None:
        self.value: Union[Any, None] = None
        super().__init__()

    def set_with_value(self, value: Any) -> None:
        self.value = value
        super().set()

    def clear(self) -> None:
        self.value = None
        super().clear()

    async def wait(self) -> Any:
        await super().wait()
        return self.value

    async def event_wait_for(self, timeout) -> Any:
        # suppress TimeoutError because we'll return False in case of timeout
        with contextlib.suppress(asyncio.TimeoutError):
            await asyncio.wait_for(self.wait(), timeout)
        return self.value if self.is_set() else None
