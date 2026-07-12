from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.repositories.booking_repository import booking_repo
from app.repositories.user_repository import user_repo
from app.repositories.employee_repository import employee_repo
from app.schemas.booking import (
    BookingCreate, BookingResponse, BookingListResponse, BookingCancelRequest,
)
from app.services.booking_service import booking_service

router = APIRouter()


async def _get_caller_emp(db, user: User):
    emp = await employee_repo.get_by_user_id(db, user.id)
    if not emp:
        raise HTTPException(status_code=403, detail="Must be an employee to book resources.")
    return emp


def _build_booking(b) -> dict:
    name = None
    if b.booked_by_employee and b.booked_by_employee.user and b.booked_by_employee.user.profile:
        p = b.booked_by_employee.user.profile
        name = f"{p.first_name} {p.last_name or ''}".strip()
    return {
        "id": b.id,
        "asset_id": b.asset_id,
        "asset_name": b.asset.name if b.asset else None,
        "asset_tag": b.asset.asset_tag if b.asset else None,
        "booked_by_name": name,
        "department_name": b.department.name if b.department else None,
        "start_datetime": b.start_datetime,
        "end_datetime": b.end_datetime,
        "purpose": b.purpose,
        "status": b.status,
        "created_at": b.created_at,
    }


@router.get("/", response_model=BookingListResponse)
async def list_bookings(
    asset_id: Optional[UUID] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    emp_filter = None
    if not asset_id:
        role = await user_repo.get_user_role_name(db, current_user.id)
        if role == "employee":
            emp = await employee_repo.get_by_user_id(db, current_user.id)
            emp_filter = emp.id if emp else None

    skip = (page - 1) * page_size
    bookings, total = await booking_repo.list_bookings(
        db, asset_id=asset_id, employee_id=emp_filter, status=status_filter,
        skip=skip, limit=page_size,
    )
    pages = (total + page_size - 1) // page_size if total > 0 else 0
    return BookingListResponse(
        items=[_build_booking(b) for b in bookings],
        total=total, page=page, page_size=page_size, pages=pages,
    )


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    payload: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    emp = await _get_caller_emp(db, current_user)
    async with db.begin_nested():
        booking = await booking_service.create_booking(
            db,
            asset_id=payload.asset_id,
            booked_by_employee_id=emp.id,
            start_datetime=payload.start_datetime,
            end_datetime=payload.end_datetime,
            purpose=payload.purpose,
            department_id=payload.department_id,
        )
    await db.commit()
    b = await booking_repo.get_by_id_with_relations(db, booking.id)
    return _build_booking(b)


@router.post("/{id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    id: UUID,
    payload: BookingCancelRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    emp = await _get_caller_emp(db, current_user)
    async with db.begin_nested():
        booking = await booking_service.cancel_booking(
            db,
            booking_id=id,
            cancelled_by_employee_id=emp.id,
            cancellation_reason=payload.cancellation_reason,
        )
    await db.commit()
    b = await booking_repo.get_by_id_with_relations(db, booking.id)
    return _build_booking(b)
