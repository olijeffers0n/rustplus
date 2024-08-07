import asyncio
import contextlib
from typing import Any, Union, Optional


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

    async def wait(self, timeout: Optional[float] = None) -> Any:
        if timeout is not None:
            with contextlib.suppress(asyncio.TimeoutError):
                await asyncio.wait_for(super().wait(), timeout)
        else:
            await super().wait()

        return self.value if self.is_set() else None

    async def event_wait_for(self, timeout: float) -> Any:
        return await self.wait(timeout)
