from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.maintenance import MaintenanceRequest, MaintenanceTechnician, MaintenanceStatusHistory
from app.models.employee import Employee
from app.models.user import User
from app.repositories.base_repository import BaseRepository


class MaintenanceRepository(BaseRepository[MaintenanceRequest]):
    def __init__(self):
        super().__init__(MaintenanceRequest)

    async def get_by_id_with_relations(self, db: AsyncSession, mr_id: UUID) -> Optional[MaintenanceRequest]:
        stmt = (
            select(MaintenanceRequest)
            .where(MaintenanceRequest.id == mr_id)
            .options(
                selectinload(MaintenanceRequest.asset),
                selectinload(MaintenanceRequest.raised_by_employee).selectinload(Employee.user).selectinload(User.profile),
                selectinload(MaintenanceRequest.approver).selectinload(Employee.user).selectinload(User.profile),
                selectinload(MaintenanceRequest.technician),
            )
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_requests(
        self,
        db: AsyncSession,
        *,
        asset_id: Optional[UUID] = None,
        status: Optional[str] = None,
        raised_by: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[MaintenanceRequest], int]:
        stmt = select(MaintenanceRequest)
        if asset_id:
            stmt = stmt.where(MaintenanceRequest.asset_id == asset_id)
        if status:
            stmt = stmt.where(MaintenanceRequest.status == status)
        if raised_by:
            stmt = stmt.where(MaintenanceRequest.raised_by_employee_id == raised_by)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar_one()

        stmt = stmt.options(
            selectinload(MaintenanceRequest.asset),
            selectinload(MaintenanceRequest.raised_by_employee).selectinload(Employee.user).selectinload(User.profile),
            selectinload(MaintenanceRequest.technician),
        ).order_by(MaintenanceRequest.created_at.desc()).offset(skip).limit(limit)

        res = await db.execute(stmt)
        return list(res.scalars().all()), total

    async def list_technicians(self, db: AsyncSession) -> List[MaintenanceTechnician]:
        stmt = select(MaintenanceTechnician).where(MaintenanceTechnician.is_active == True).order_by(MaintenanceTechnician.name)
        res = await db.execute(stmt)
        return list(res.scalars().all())


maintenance_repo = MaintenanceRepository()
