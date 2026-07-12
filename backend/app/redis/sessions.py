"""
app/redis/sessions.py
──────────────────────
Session storage helpers for OTP / temporary auth state in Redis.
No business logic — pure key-value store wrappers.
"""

import json
from typing import Any, Optional

from app.core.constants import REDIS_PREFIX_OTP, REDIS_PREFIX_SESSION
from app.redis.client import get_redis_client


async def session_set(session_id: str, data: dict, ttl: int = 3600) -> None:
    """Persist a session dict under *session_id* with a TTL."""
    client = await get_redis_client()
    await client.setex(
        f"{REDIS_PREFIX_SESSION}{session_id}",
        ttl,
        json.dumps(data),
    )


async def session_get(session_id: str) -> Optional[dict]:
    """Retrieve session data. Returns None if missing or expired."""
    client = await get_redis_client()
    raw = await client.get(f"{REDIS_PREFIX_SESSION}{session_id}")
    return json.loads(raw) if raw else None


async def session_delete(session_id: str) -> None:
    """Invalidate a session."""
    client = await get_redis_client()
    await client.delete(f"{REDIS_PREFIX_SESSION}{session_id}")


# ── OTP / temporary token storage ─────────────────────────────────────────────

async def otp_set(identifier: str, otp: str, ttl: int = 300) -> None:
    """Store an OTP for *identifier* (e.g. email) with a short TTL."""
    client = await get_redis_client()
    await client.setex(f"{REDIS_PREFIX_OTP}{identifier}", ttl, otp)


async def otp_get(identifier: str) -> Optional[str]:
    """Retrieve the current OTP for *identifier*. Returns None if expired."""
    client = await get_redis_client()
    return await client.get(f"{REDIS_PREFIX_OTP}{identifier}")


async def otp_delete(identifier: str) -> None:
    """Delete an OTP after successful verification."""
    client = await get_redis_client()
    await client.delete(f"{REDIS_PREFIX_OTP}{identifier}")
