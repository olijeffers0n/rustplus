import time

class TokenBucket:

   def __init__(self, current: int, maximum: int, refresh_rate, refresh_amount) -> None:

        self.current = current
        self.max = maximum
        self.refresh_rate = refresh_rate
        self.refresh_amount = refresh_amount

   def can_consume(self, amount) -> bool:

        if (self.current - amount) >= 0:
            return True

        return False

   def consume(self, amount: int = 1) -> None:

        self.current -= amount

   def refresh(self, amount = None) -> None:

        if amount is None:
            amount = self.refresh_amount

        if amount > self.max:
            self.current = self.max
        elif (self.max - self.current) > amount:
            self.current += amount
        else:
            self.current = self.max

class RateLimiter:

    def __init__(self, current : int, maximum : int, refresh_rate, refresh_amount) -> None:
        
        self.bucket = TokenBucket(current=current, maximum=maximum, refresh_rate=refresh_rate, refresh_amount=refresh_amount)
        self.last_consumed = 0

    def can_consume(self, amount: int = 1) -> bool:
        """
        Returns whether the user can comsume the amount of tokens provided
        """
        return self.bucket.can_consume(amount)

    def scale_amount_to_time_delta(self, delta) -> float:
        """
        Scales the refresh amount to a given time delta
        """
        return self.bucket.refresh_amount * (delta / self.bucket.refresh_rate)

    def consume(self, amount: int = 1) -> None:
        """
        Consumes an amount of tokens from the bucket. You should first check to see whether it is possible with can_consume
        """
        time_now = time.time()

        self.bucket.refresh(amount=self.scale_amount_to_time_delta(time_now-self.last_consumed))

        self.last_consumed = time_now

        self.bucket.consume(amount=amount)
