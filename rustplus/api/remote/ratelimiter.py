import math
import time
import threading
from typing import Dict

from ...exceptions.exceptions import RateLimitError
from ...utils import ServerID


class TokenBucket:
    def __init__(
        self, current: float, maximum: float, refresh_rate: float, refresh_amount: float
    ) -> None:
        self.current = current
        self.max = maximum
        self.refresh_rate = refresh_rate
        self.refresh_amount = refresh_amount
        self.last_update = time.time()
        self.refresh_per_second = self.refresh_amount / self.refresh_rate

    def can_consume(self, amount) -> bool:
        if (self.current - amount) >= 0:
            return True

        return False

    def consume(self, amount: int = 1) -> None:
        self.current -= amount

    def refresh(self) -> None:
        time_now = time.time()

        time_delta = time_now - self.last_update
        self.last_update = time_now

        self.current = min([self.current + time_delta * self.refresh_amount, self.max])


class RateLimiter:

    SERVER_LIMIT = 50
    SERVER_REFRESH_AMOUNT = 15

    @classmethod
    def default(cls) -> "RateLimiter":
        """
        Returns a default rate limiter with 3 tokens per second
        """
        return cls()

    def __init__(self) -> None:
        self.socket_buckets: Dict[ServerID, TokenBucket] = {}
        self.server_buckets: Dict[str, TokenBucket] = {}
        self.lock = threading.Lock()

    def add_socket(
        self,
        server_id: ServerID,
        current: float,
        maximum: float,
        refresh_rate: float,
        refresh_amount: float,
    ) -> None:
        self.socket_buckets[server_id] = TokenBucket(
            current, maximum, refresh_rate, refresh_amount
        )
        if server_id.get_server_string() not in self.server_buckets:
            self.server_buckets[server_id.get_server_string()] = TokenBucket(
                self.SERVER_LIMIT, self.SERVER_LIMIT, 1, self.SERVER_REFRESH_AMOUNT
            )

    def can_consume(self, server_id: ServerID, amount: int = 1) -> bool:
        """
        Returns whether the user can consume the amount of tokens provided
        """
        self.lock.acquire(blocking=True)
        can_consume = True

        for bucket in [
            self.socket_buckets.get(server_id),
            self.server_buckets.get(server_id.get_server_string()),
        ]:
            bucket.refresh()
            if not bucket.can_consume(amount):
                can_consume = False

        self.lock.release()
        return can_consume

    def consume(self, server_id: ServerID, amount: int = 1) -> None:
        """
        Consumes an amount of tokens from the bucket. You should first check to see whether it is possible with can_consume
        """
        self.lock.acquire(blocking=True)
        for bucket in [
            self.socket_buckets.get(server_id),
            self.server_buckets.get(server_id.get_server_string()),
        ]:
            bucket.refresh()
            if not bucket.can_consume(amount):
                self.lock.release()
                raise RateLimitError("Not Enough Tokens")
            bucket.consume(amount)
        self.lock.release()

    def get_estimated_delay_time(self, server_id: ServerID, target_cost: int) -> float:
        """
        Returns how long until the amount of tokens needed will be available
        """
        self.lock.acquire(blocking=True)
        delay = 0
        for bucket in [
            self.socket_buckets.get(server_id),
            self.server_buckets.get(server_id.get_server_string()),
        ]:
            val = (
                math.ceil(
                    (((target_cost - bucket.current) / bucket.refresh_per_second) + 0.1)
                    * 100
                )
                / 100
            )
            if val > delay:
                delay = val
        self.lock.release()
        return delay

    def remove(self, server_id: ServerID) -> None:
        """
        Removes the limiter
        """
        self.lock.acquire(blocking=True)
        del self.socket_buckets[server_id]
        self.lock.release()
