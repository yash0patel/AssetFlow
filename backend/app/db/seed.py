"""
app/db/seed.py
───────────────
Database seeding script for local development.
Run: python -m app.db.seed
No business logic — just a placeholder for initial seed data.
"""

import asyncio

from app.db.database import AsyncSessionLocal


async def seed() -> None:
    """Seed the database with initial development data."""
    async with AsyncSessionLocal() as session:
        # TODO: Add seed data when models are implemented
        print("Database seeding complete (no-op for now).")
        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
