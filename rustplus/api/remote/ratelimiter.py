import math
import time
import threading

from ...exceptions.exceptions import RateLimitError


class TokenBucket:
    def __init__(
        self, current: int, maximum: int, refresh_rate, refresh_amount
    ) -> None:
        self.current = current
        self.max = maximum
        self.refresh_rate = refresh_rate
        self.refresh_amount = refresh_amount
        self.last_update = time.time()

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
        return cls(25, 25, 1, 3)

    def __init__(
        self, current: int, maximum: int, refresh_rate, refresh_amount
    ) -> None:
        self.bucket = TokenBucket(
            current=current,
            maximum=maximum,
            refresh_rate=refresh_rate,
            refresh_amount=refresh_amount,
        )
        self.refresh_per_second = self.bucket.refresh_amount / self.bucket.refresh_rate
        self.lock = threading.Lock()

    def can_consume(self, amount: int = 1) -> bool:
        """
        Returns whether the user can consume the amount of tokens provided
        """
        self.lock.acquire(blocking=True)
        self.bucket.refresh()
        can_consume = self.bucket.can_consume(amount)
        self.lock.release()
        return can_consume

    def consume(self, amount: int = 1) -> None:
        """
        Consumes an amount of tokens from the bucket. You should first check to see whether it is possible with can_consume
        """
        self.lock.acquire(blocking=True)
        self.bucket.refresh()
        if not self.can_consume(amount):
            self.lock.release()
            raise RateLimitError("Not Enough Tokens")
        self.bucket.consume(amount)
        self.lock.release()

    def get_estimated_delay_time(self, target_cost: int) -> float:
        """
        Returns how long until the amount of tokens needed will be available
        """
        self.lock.acquire(blocking=True)
        val = (
            math.ceil(
                (((target_cost - self.bucket.current) / self.refresh_per_second) + 0.1)
                * 100
            )
            / 100
        )
        self.lock.release()
        return val

    def reset(self) -> None:
        """
        Resets the limiter, filling the bucket to max.
        """
        self.lock.acquire(blocking=True)
        self.bucket.last_update = time.time()
        self.bucket.current = self.bucket.max
        self.lock.release()
