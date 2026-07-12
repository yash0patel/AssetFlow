"""
app/utils/helpers.py
─────────────────────
Generic utility helpers used across the application.
"""

import uuid
from datetime import datetime, timezone


def generate_uuid() -> str:
    """Return a new UUID4 string."""
    return str(uuid.uuid4())


def utcnow() -> datetime:
    """Return the current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


def paginate(items: list, page: int, page_size: int) -> dict:
    """
    Return a pagination envelope for a list of items.

    Note: For database queries prefer offset/limit at the query level.
    This helper is for in-memory slicing only.
    """
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "items": items[start:end],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
    }
