from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.repositories.base_repository import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self):
        super().__init__(Notification)

    async def list_notifications(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        category: Optional[str] = None,
        is_read: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Notification], int, int]:
        stmt = select(Notification).where(Notification.recipient_user_id == user_id)
        if category:
            stmt = stmt.where(Notification.category == category)
        if is_read is not None:
            stmt = stmt.where(Notification.is_read == is_read)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar_one()

        # Unread count
        unread = (await db.execute(
            select(func.count(Notification.id)).where(
                Notification.recipient_user_id == user_id,
                Notification.is_read == False
            )
        )).scalar_one()

        stmt = stmt.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars().all()), total, unread

    async def mark_read(self, db: AsyncSession, notification_id: int, user_id: UUID) -> Optional[Notification]:
        n = await db.get(Notification, notification_id)
        if n and n.recipient_user_id == user_id and not n.is_read:
            n.is_read = True
            n.read_at = datetime.now(timezone.utc)
            await db.flush()
        return n

    async def mark_all_read(self, db: AsyncSession, user_id: UUID) -> int:
        from sqlalchemy import update
        stmt = (
            update(Notification)
            .where(Notification.recipient_user_id == user_id, Notification.is_read == False)
            .values(is_read=True, read_at=datetime.now(timezone.utc))
        )
        res = await db.execute(stmt)
        return res.rowcount

    async def create_notification(
        self,
        db: AsyncSession,
        *,
        recipient_user_id: UUID,
        notification_type: str,
        category: str,
        title: str,
        message: str,
        reference_type: Optional[str] = None,
        reference_id: Optional[UUID] = None,
    ) -> Notification:
        n = Notification(
            recipient_user_id=recipient_user_id,
            notification_type=notification_type,
            category=category,
            title=title,
            message=message,
            reference_type=reference_type,
            reference_id=reference_id,
        )
        db.add(n)
        await db.flush()
        return n


notification_repo = NotificationRepository()
