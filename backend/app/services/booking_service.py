from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import ResourceBooking
from app.repositories.booking_repository import booking_repo


class BookingService:
    async def create_booking(
        self,
        db: AsyncSession,
        *,
        asset_id: UUID,
        booked_by_employee_id: UUID,
        start_datetime: datetime,
        end_datetime: datetime,
        purpose: Optional[str] = None,
        department_id: Optional[UUID] = None,
    ) -> ResourceBooking:
        # Overlap validation
        has_overlap = await booking_repo.check_overlap(db, asset_id, start_datetime, end_datetime)
        if has_overlap:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="The requested time slot overlaps with an existing booking for this resource.",
            )

        booking = ResourceBooking(
            asset_id=asset_id,
            booked_by_employee_id=booked_by_employee_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            purpose=purpose,
            department_id=department_id,
            status="Upcoming",
        )
        db.add(booking)
        await db.flush()
        return booking

    async def cancel_booking(
        self,
        db: AsyncSession,
        *,
        booking_id: UUID,
        cancelled_by_employee_id: UUID,
        cancellation_reason: Optional[str] = None,
    ) -> ResourceBooking:
        booking = await booking_repo.get(db, booking_id)
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found.")
        if booking.status not in ("Upcoming", "Ongoing"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel a booking with status '{booking.status}'.",
            )
        booking.status = "Cancelled"
        booking.cancelled_by = cancelled_by_employee_id
        booking.cancelled_at = datetime.now(timezone.utc)
        booking.cancellation_reason = cancellation_reason
        booking.updated_at = datetime.now(timezone.utc)
        await db.flush()
        return booking


booking_service = BookingService()
