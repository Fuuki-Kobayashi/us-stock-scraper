import asyncio
import time

import pytest

from app.utils.rate_limiter import RateLimiter


@pytest.mark.asyncio
async def test_rate_limiter_immediate_acquire():
    limiter = RateLimiter(max_tokens=5, refill_rate=5 / 60)
    # First 5 calls should be immediate
    for _ in range(5):
        await limiter.acquire()


@pytest.mark.asyncio
async def test_rate_limiter_throttle():
    limiter = RateLimiter(max_tokens=2, refill_rate=100.0)  # Fast refill for test
    # Exhaust tokens
    await limiter.acquire()
    await limiter.acquire()
    # Third call should wait briefly then succeed
    start = time.monotonic()
    await limiter.acquire()
    elapsed = time.monotonic() - start
    # With fast refill, should be very quick
    assert elapsed < 1.0


@pytest.mark.asyncio
async def test_rate_limiter_refill():
    limiter = RateLimiter(max_tokens=1, refill_rate=1000.0)  # Very fast refill
    await limiter.acquire()
    # Should refill quickly
    await asyncio.sleep(0.01)
    await limiter.acquire()  # Should succeed after refill
