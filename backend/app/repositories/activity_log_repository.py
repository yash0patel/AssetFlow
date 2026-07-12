from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.activity_log import ActivityLog
from app.models.user import User, UserProfile
from app.repositories.base_repository import BaseRepository


class ActivityLogRepository(BaseRepository[ActivityLog]):
    def __init__(self):
        super().__init__(ActivityLog)

    async def list_logs(
        self,
        db: AsyncSession,
        *,
        entity_type: Optional[str] = None,
        actor_user_id: Optional[UUID] = None,
        action: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[ActivityLog], int]:
        stmt = select(ActivityLog)
        if entity_type:
            stmt = stmt.where(ActivityLog.entity_type == entity_type)
        if actor_user_id:
            stmt = stmt.where(ActivityLog.actor_user_id == actor_user_id)
        if action:
            stmt = stmt.where(ActivityLog.action == action)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar_one()

        stmt = stmt.options(
            selectinload(ActivityLog.actor_user).selectinload(User.profile)
        ).order_by(ActivityLog.created_at.desc()).offset(skip).limit(limit)

        res = await db.execute(stmt)
        return list(res.scalars().all()), total

    async def log(
        self,
        db: AsyncSession,
        *,
        actor_user_id: Optional[UUID],
        actor_role: Optional[str],
        action: str,
        module_name: str,
        entity_type: str,
        entity_id: Optional[UUID] = None,
        description: Optional[str] = None,
        old_value: Optional[dict] = None,
        new_value: Optional[dict] = None,
    ) -> None:
        entry = ActivityLog(
            actor_user_id=actor_user_id,
            actor_role=actor_role,
            action=action,
            module_name=module_name,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value or ({"description": description} if description else None),
        )
        db.add(entry)
        await db.flush()


activity_log_repo = ActivityLogRepository()
