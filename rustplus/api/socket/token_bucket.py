from .repeated_timer import RepeatedTimer


class TokenBucket:

   def __init__(self, current: int, maximum: int, refresh_rate, refresh_amount) -> None:

        self.current = current
        self.max = maximum
        self.refresh_rate = refresh_rate
        self.refresh_amount = refresh_amount

        self.refiller = RepeatedTimer(self.refresh_rate, self.refresh)

   def can_consume(self, amount: int = 1) -> bool:

        if (self.current - amount) >= 0:
            return True

        return False

   def consume(self, amount: int = 1) -> None:

        self.current -= amount

   def refresh(self) -> None:

        if (self.max - self.current) > self.refresh_amount:
            self.current += self.refresh_amount
        else:
            self.current = self.max