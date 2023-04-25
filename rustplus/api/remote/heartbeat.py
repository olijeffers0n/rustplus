import asyncio
import time


class HeartBeat:
    def __init__(self, rust_api) -> None:

        self.rust_api = rust_api
        self.next_run = time.time()
        self.running = False

    async def start_beat(self) -> None:

        if self.running:
            return

        self.running = True

        asyncio.create_task(self._heart_beat())

    async def _heart_beat(self) -> None:

        while True:

            if time.time() >= self.next_run:

                await self.beat()

            else:
                await asyncio.sleep(1)

    async def beat(self) -> None:

        if self.rust_api.remote.ws is not None and self.rust_api.remote.is_open():
            await self.rust_api.send_wakeup_request()

    def reset_rhythm(self) -> None:

        self.next_run = time.time() + 240
