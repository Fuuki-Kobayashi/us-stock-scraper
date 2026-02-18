import asyncio
import time


class RateLimiter:
    """Token bucket rate limiter for API calls."""

    def __init__(self, max_tokens: int = 5, refill_rate: float = 5 / 60) -> None:
        self._max_tokens = max_tokens
        self._refill_rate = refill_rate  # tokens per second
        self._tokens = float(max_tokens)
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(
            self._max_tokens, self._tokens + elapsed * self._refill_rate
        )
        self._last_refill = now

    async def acquire(self) -> None:
        async with self._lock:
            self._refill()
            if self._tokens < 1:
                wait_time = (1 - self._tokens) / self._refill_rate
                await asyncio.sleep(wait_time)
                self._refill()
            self._tokens -= 1
