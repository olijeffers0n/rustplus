import asyncio
import time
import threading

class HeartBeat:

    def __init__(self, rust_api) -> None:

        self.rust_api = rust_api
        self.next_run = time.time()
        self.running = False

    async def start_beat(self) -> None:

        if self.running:
            return 

        def wrapper(self, loop) -> None:

            async def heart_beat(self) -> None:

                while True:
                    if time.time() >= self.next_run:

                        await self.beat()

                        self.reset_rythm()
                        
                    await asyncio.sleep(1)

            asyncio.run_coroutine_threadsafe(heart_beat(self), loop)

        thread = threading.Thread(target=wrapper, args=[self, asyncio.get_event_loop()])
        thread.daemon = True
        thread.start()

    async def beat(self) -> None:

        if self.rust_api.remote.ws is not None:

            await self.rust_api._send_wakeup_request()

    def reset_rythm(self) -> None:

        self.next_run = time.time() + 300
