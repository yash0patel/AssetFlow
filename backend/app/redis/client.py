"""
app/redis/client.py
────────────────────
Redis async client singleton.
Import `get_redis_client` anywhere caching / sessions are needed.
"""

import redis.asyncio as aioredis
from redis.asyncio import Redis

from app.core.config import settings

# Module-level pool — created once, reused across requests
_redis_pool: Redis | None = None


async def get_redis_client() -> Redis:
    """
    Return a connected async Redis client backed by a connection pool.

    The client is initialised lazily on first call and cached globally.
    """
    global _redis_pool

    if _redis_pool is None:
        kwargs: dict = {
            "decode_responses": True,
        }
        if settings.REDIS_PASSWORD:
            kwargs["password"] = settings.REDIS_PASSWORD

        _redis_pool = aioredis.from_url(settings.REDIS_URL, **kwargs)

    return _redis_pool


async def close_redis_client() -> None:
    """Close the Redis connection pool. Called on application shutdown."""
    global _redis_pool
    if _redis_pool is not None:
        await _redis_pool.aclose()
        _redis_pool = None
