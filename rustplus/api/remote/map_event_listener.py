import asyncio
import threading
import time

from ..structures import MarkerEvent


class MapEventListener:
    def __init__(self, api) -> None:
        self.api = api
        self.thread = None
        self.gc = None
        self.loop = asyncio.get_event_loop_policy().get_event_loop()
        self._iter_delay = 5
        self.persistent_ids = {}
        self.highest_id = 0
        self.listeners = []

    def add_listener(self, listener) -> None:
        self.listeners.append(listener)

    def remove_listener(self, listener) -> bool:
        try:
            self.listeners.remove(listener)
            return True
        except ValueError:
            return False

    def start(self, delay) -> None:
        self._iter_delay = delay
        self.thread = threading.Thread(
            target=self._run, daemon=True, name="MapEventListener"
        )
        self.thread.start()
        self.gc = IDGarbageCollector(self.persistent_ids)
        self.gc.start()

    def _run(self) -> None:

        while True:

            try:

                future = asyncio.run_coroutine_threadsafe(
                    self.api.get_markers(), self.loop
                )
                new_highest_id = 0
                for marker in future.result():

                    new = False

                    if marker.id in self.persistent_ids:
                        self.call_event(marker, new)
                        continue

                    if marker.id > self.highest_id:
                        new = True
                        if marker.id > new_highest_id:
                            new_highest_id = marker.id

                    # Removal Times
                    removal_time = time.time()

                    if marker.type == 3 or marker.type == 1:
                        removal_time = float("inf")
                    else:
                        removal_time += 120 * 60

                    self.persistent_ids[marker.id] = removal_time

                    self.call_event(marker, new)

                self.highest_id = new_highest_id

            except Exception as e:
                print(e)

            time.sleep(self._iter_delay)

    def call_event(self, marker, is_new) -> None:
        for listener in self.listeners:
            asyncio.run_coroutine_threadsafe(
                listener.get_coro()(MarkerEvent(marker, is_new)), self.loop
            )


class IDGarbageCollector:
    def __init__(self, target: dict) -> None:
        self.target = target
        self.thread = None

    def start(self) -> None:
        self.thread = threading.Thread(
            target=self._run, daemon=True, name="IDGarbageCollector"
        )
        self.thread.start()

    def _run(self) -> None:
        while True:
            try:
                for key in list(self.target.keys()):
                    if self.target[key] < time.time():
                        del self.target[key]
            except Exception as e:
                print(e)
            time.sleep(5)
