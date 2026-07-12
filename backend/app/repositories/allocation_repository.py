from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime, timezone, date

from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.allocation import AssetAllocation
from app.models.asset import Asset
from app.models.employee import Employee
from app.models.department import Department
from app.models.user import User, UserProfile
from app.repositories.base_repository import BaseRepository


class AllocationRepository(BaseRepository[AssetAllocation]):
    def __init__(self):
        super().__init__(AssetAllocation)

    async def get_active_allocation_for_asset(
        self, db: AsyncSession, asset_id: UUID
    ) -> Optional[AssetAllocation]:
        """Return the single active allocation for an asset, or None."""
        stmt = (
            select(AssetAllocation)
            .where(
                AssetAllocation.asset_id == asset_id,
                AssetAllocation.status == "Active",
            )
            .options(
                selectinload(AssetAllocation.allocated_to_employee).selectinload(Employee.user).selectinload(User.profile),
                selectinload(AssetAllocation.allocated_to_department),
                selectinload(AssetAllocation.asset),
            )
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_id_with_relations(self, db: AsyncSession, alloc_id: UUID) -> Optional[AssetAllocation]:
        stmt = (
            select(AssetAllocation)
            .where(AssetAllocation.id == alloc_id)
            .options(
                selectinload(AssetAllocation.asset),
                selectinload(AssetAllocation.allocated_to_employee).selectinload(Employee.user).selectinload(User.profile),
                selectinload(AssetAllocation.allocated_to_department),
                selectinload(AssetAllocation.allocator).selectinload(Employee.user).selectinload(User.profile),
            )
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_allocations(
        self,
        db: AsyncSession,
        *,
        employee_id: Optional[UUID] = None,
        department_id: Optional[UUID] = None,
        asset_id: Optional[UUID] = None,
        status: Optional[str] = None,
        overdue_only: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[AssetAllocation], int]:
        stmt = select(AssetAllocation)

        if employee_id:
            stmt = stmt.where(AssetAllocation.allocated_to_employee_id == employee_id)
        if department_id:
            stmt = stmt.where(AssetAllocation.allocated_to_department_id == department_id)
        if asset_id:
            stmt = stmt.where(AssetAllocation.asset_id == asset_id)
        if status:
            stmt = stmt.where(AssetAllocation.status == status)
        if overdue_only:
            today = datetime.now(timezone.utc).date()
            stmt = stmt.where(
                AssetAllocation.status == "Active",
                AssetAllocation.expected_return_date < today,
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar_one()

        stmt = stmt.options(
            selectinload(AssetAllocation.asset),
            selectinload(AssetAllocation.allocated_to_employee).selectinload(Employee.user).selectinload(User.profile),
            selectinload(AssetAllocation.allocated_to_department),
            selectinload(AssetAllocation.allocator).selectinload(Employee.user).selectinload(User.profile),
        ).order_by(AssetAllocation.allocation_date.desc()).offset(skip).limit(limit)

        res = await db.execute(stmt)
        return list(res.scalars().all()), total


allocation_repo = AllocationRepository()
