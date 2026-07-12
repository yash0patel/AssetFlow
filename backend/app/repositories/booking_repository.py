from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.booking import ResourceBooking
from app.models.employee import Employee
from app.models.user import User
from app.repositories.base_repository import BaseRepository


class BookingRepository(BaseRepository[ResourceBooking]):
    def __init__(self):
        super().__init__(ResourceBooking)

    async def get_by_id_with_relations(self, db: AsyncSession, booking_id: UUID) -> Optional[ResourceBooking]:
        stmt = (
            select(ResourceBooking)
            .where(ResourceBooking.id == booking_id)
            .options(
                selectinload(ResourceBooking.asset),
                selectinload(ResourceBooking.booked_by_employee).selectinload(Employee.user).selectinload(User.profile),
                selectinload(ResourceBooking.department),
            )
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def check_overlap(
        self,
        db: AsyncSession,
        asset_id: UUID,
        start: datetime,
        end: datetime,
        exclude_id: Optional[UUID] = None,
    ) -> bool:
        """Return True if there's any non-cancelled overlap for the asset."""
        stmt = select(func.count()).select_from(
            select(ResourceBooking)
            .where(
                ResourceBooking.asset_id == asset_id,
                ResourceBooking.status != "Cancelled",
                ResourceBooking.start_datetime < end,
                ResourceBooking.end_datetime > start,
            )
            .subquery()
        )
        if exclude_id:
            stmt = select(func.count()).select_from(
                select(ResourceBooking)
                .where(
                    ResourceBooking.asset_id == asset_id,
                    ResourceBooking.status != "Cancelled",
                    ResourceBooking.id != exclude_id,
                    ResourceBooking.start_datetime < end,
                    ResourceBooking.end_datetime > start,
                )
                .subquery()
            )
        count = (await db.execute(stmt)).scalar_one()
        return count > 0

    async def list_bookings(
        self,
        db: AsyncSession,
        *,
        asset_id: Optional[UUID] = None,
        employee_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[ResourceBooking], int]:
        stmt = select(ResourceBooking)
        if asset_id:
            stmt = stmt.where(ResourceBooking.asset_id == asset_id)
        if employee_id:
            stmt = stmt.where(ResourceBooking.booked_by_employee_id == employee_id)
        if status:
            stmt = stmt.where(ResourceBooking.status == status)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar_one()

        stmt = stmt.options(
            selectinload(ResourceBooking.asset),
            selectinload(ResourceBooking.booked_by_employee).selectinload(Employee.user).selectinload(User.profile),
            selectinload(ResourceBooking.department),
        ).order_by(ResourceBooking.start_datetime.desc()).offset(skip).limit(limit)

        res = await db.execute(stmt)
        return list(res.scalars().all()), total


booking_repo = BookingRepository()
