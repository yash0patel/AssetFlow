"""
app/redis/rate_limit.py
────────────────────────
Sliding-window rate limiter using Redis INCR + EXPIRE.
No business logic — pure infrastructure helper.
"""

from app.core.constants import (
    RATE_LIMIT_REQUESTS,
    RATE_LIMIT_WINDOW,
    REDIS_PREFIX_RATE_LIMIT,
)
from app.redis.client import get_redis_client


async def is_rate_limited(
    identifier: str,
    max_requests: int = RATE_LIMIT_REQUESTS,
    window_seconds: int = RATE_LIMIT_WINDOW,
) -> bool:
    """
    Check and increment request count for *identifier*.

    Returns True if the caller has exceeded the allowed request rate.

    Args:
        identifier:     Unique key (e.g. IP address, user id).
        max_requests:   Maximum requests allowed in *window_seconds*.
        window_seconds: Length of the rate limit window in seconds.
    """
    client = await get_redis_client()
    key = f"{REDIS_PREFIX_RATE_LIMIT}{identifier}"

    count: int = await client.incr(key)
    if count == 1:
        # First request in this window — set expiry
        await client.expire(key, window_seconds)

    return count > max_requests


async def get_remaining_requests(
    identifier: str,
    max_requests: int = RATE_LIMIT_REQUESTS,
) -> int:
    """Return how many requests remain in the current window for *identifier*."""
    client = await get_redis_client()
    key = f"{REDIS_PREFIX_RATE_LIMIT}{identifier}"
    count_raw = await client.get(key)
    count = int(count_raw) if count_raw else 0
    return max(0, max_requests - count)


async def reset_rate_limit(identifier: str) -> None:
    """Reset the rate limit counter for *identifier* (e.g. after auth success)."""
    client = await get_redis_client()
    await client.delete(f"{REDIS_PREFIX_RATE_LIMIT}{identifier}")
