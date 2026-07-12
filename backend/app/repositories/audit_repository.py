from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.audit import AuditCycle, AuditCycleAuditor, AuditCycleItem, AuditDiscrepancyReport
from app.models.employee import Employee
from app.models.user import User
from app.repositories.base_repository import BaseRepository


class AuditRepository(BaseRepository[AuditCycle]):
    def __init__(self):
        super().__init__(AuditCycle)

    async def get_by_id_with_relations(self, db: AsyncSession, cycle_id: UUID) -> Optional[AuditCycle]:
        stmt = (
            select(AuditCycle)
            .where(AuditCycle.id == cycle_id)
            .options(
                selectinload(AuditCycle.scope_department),
                selectinload(AuditCycle.scope_location),
                selectinload(AuditCycle.creator).selectinload(Employee.user).selectinload(User.profile),
                selectinload(AuditCycle.auditors).selectinload(AuditCycleAuditor.employee).selectinload(Employee.user).selectinload(User.profile),
                selectinload(AuditCycle.items).selectinload(AuditCycleItem.asset),
            )
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_cycles(
        self,
        db: AsyncSession,
        *,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[AuditCycle], int]:
        stmt = select(AuditCycle)
        if status:
            stmt = stmt.where(AuditCycle.status == status)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar_one()

        stmt = stmt.options(
            selectinload(AuditCycle.scope_department),
            selectinload(AuditCycle.creator).selectinload(Employee.user).selectinload(User.profile),
            selectinload(AuditCycle.auditors),
            selectinload(AuditCycle.items),
        ).order_by(AuditCycle.created_at.desc()).offset(skip).limit(limit)

        res = await db.execute(stmt)
        return list(res.scalars().all()), total

    async def get_items(self, db: AsyncSession, cycle_id: UUID) -> List[AuditCycleItem]:
        stmt = (
            select(AuditCycleItem)
            .where(AuditCycleItem.audit_cycle_id == cycle_id)
            .options(
                selectinload(AuditCycleItem.asset),
                selectinload(AuditCycleItem.verifier).selectinload(Employee.user).selectinload(User.profile),
            )
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def get_item(self, db: AsyncSession, item_id: int) -> Optional[AuditCycleItem]:
        stmt = (
            select(AuditCycleItem)
            .where(AuditCycleItem.id == item_id)
            .options(selectinload(AuditCycleItem.asset), selectinload(AuditCycleItem.verifier))
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()


audit_repo = AuditRepository()
