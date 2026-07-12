"""
app/redis/cache.py
───────────────────
Generic JSON cache helpers built on top of the Redis client.
No business logic — pure infrastructure.
"""

import json
from typing import Any, Optional

from app.core.constants import CACHE_TTL_MEDIUM, REDIS_PREFIX_CACHE
from app.redis.client import get_redis_client


async def cache_set(key: str, value: Any, ttl: int = CACHE_TTL_MEDIUM) -> None:
    """
    Serialize *value* to JSON and store it under *key* with a TTL.

    Args:
        key:   Cache key (will be prefixed automatically).
        value: Any JSON-serialisable Python value.
        ttl:   Time-to-live in seconds.
    """
    client = await get_redis_client()
    full_key = f"{REDIS_PREFIX_CACHE}{key}"
    await client.setex(full_key, ttl, json.dumps(value))


async def cache_get(key: str) -> Optional[Any]:
    """
    Retrieve and deserialise the cached value for *key*.

    Returns None if the key does not exist or has expired.
    """
    client = await get_redis_client()
    full_key = f"{REDIS_PREFIX_CACHE}{key}"
    raw = await client.get(full_key)
    if raw is None:
        return None
    return json.loads(raw)


async def cache_delete(key: str) -> None:
    """Delete a single cache entry."""
    client = await get_redis_client()
    await client.delete(f"{REDIS_PREFIX_CACHE}{key}")


async def cache_delete_pattern(pattern: str) -> None:
    """
    Delete all cache keys matching *pattern*.

    Example: ``cache_delete_pattern("departments:*")``
    """
    client = await get_redis_client()
    full_pattern = f"{REDIS_PREFIX_CACHE}{pattern}"
    keys = await client.keys(full_pattern)
    if keys:
        await client.delete(*keys)
