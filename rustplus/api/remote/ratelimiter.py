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
    @classmethod
    def default(cls) -> "RateLimiter":
        """
        Returns a default rate limiter with 3 tokens per second
        """
        return cls()

    def __init__(self) -> None:
        self.buckets: Dict[ServerID, TokenBucket] = {}
        self.lock = threading.Lock()

    def add_socket(
        self,
        server_id: ServerID,
        current: float,
        maximum: float,
        refresh_rate: float,
        refresh_amount: float,
    ) -> None:
        self.buckets[server_id] = TokenBucket(
            current, maximum, refresh_rate, refresh_amount
        )

    def can_consume(self, server_id: ServerID, amount: int = 1) -> bool:
        """
        Returns whether the user can consume the amount of tokens provided
        """
        self.lock.acquire(blocking=True)
        bucket = self.buckets.get(server_id)
        bucket.refresh()
        can_consume = bucket.can_consume(amount)
        self.lock.release()
        return can_consume

    def consume(self, server_id: ServerID, amount: int = 1) -> None:
        """
        Consumes an amount of tokens from the bucket. You should first check to see whether it is possible with can_consume
        """
        self.lock.acquire(blocking=True)
        bucket = self.buckets.get(server_id)
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
        bucket = self.buckets.get(server_id)
        val = (
            math.ceil(
                (((target_cost - bucket.current) / bucket.refresh_per_second) + 0.1)
                * 100
            )
            / 100
        )
        self.lock.release()
        return val

    def reset(self, server_id: ServerID) -> None:
        """
        Resets the limiter, filling the bucket to max.
        """
        self.lock.acquire(blocking=True)
        bucket = self.buckets.get(server_id)
        bucket.last_update = time.time()
        bucket.current = bucket.max
        self.lock.release()
