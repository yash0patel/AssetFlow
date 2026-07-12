from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.repositories.allocation_repository import allocation_repo
from app.repositories.transfer_repository import transfer_repo
from app.repositories.user_repository import user_repo
from app.repositories.employee_repository import employee_repo
from app.schemas.allocation import (
    AllocationCreate, ReturnRequest, AllocationResponse, AllocationListResponse,
    TransferRequestCreate, TransferResponse, TransferListResponse, TransferActionRequest,
)
from app.services.allocation_service import allocation_service

router = APIRouter()


async def _get_caller_employee(db, user: User):
    emp = await employee_repo.get_by_user_id(db, user.id)
    if not emp:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You must be an employee to perform this action.")
    return emp


async def _require_manager(db, user: User):
    role = await user_repo.get_user_role_name(db, user.id)
    if role not in ("admin", "asset_manager", "department_head"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Manager, Department Head, or Admin access required.")


def _emp_name(emp) -> Optional[str]:
    if emp and emp.user and emp.user.profile:
        p = emp.user.profile
        return f"{p.first_name} {p.last_name or ''}".strip()
    return None


def _build_alloc(alloc) -> dict:
    from datetime import date
    is_overdue = False
    if alloc.status == "Active" and alloc.expected_return_date:
        is_overdue = alloc.expected_return_date < datetime.now(timezone.utc).date()

    return {
        "id": alloc.id,
        "asset_id": alloc.asset_id,
        "asset_tag": alloc.asset.asset_tag if alloc.asset else None,
        "asset_name": alloc.asset.name if alloc.asset else None,
        "allocated_to_employee_id": alloc.allocated_to_employee_id,
        "allocated_to_employee_name": _emp_name(alloc.allocated_to_employee),
        "allocated_to_department_id": alloc.allocated_to_department_id,
        "allocated_to_department_name": alloc.allocated_to_department.name if alloc.allocated_to_department else None,
        "allocated_by_name": _emp_name(alloc.allocator),
        "allocation_date": alloc.allocation_date,
        "expected_return_date": alloc.expected_return_date,
        "actual_return_date": alloc.actual_return_date,
        "return_condition": alloc.return_condition,
        "return_notes": alloc.return_notes,
        "status": alloc.status,
        "is_overdue": is_overdue,
        "created_at": alloc.created_at,
    }


def _build_transfer(tr) -> dict:
    return {
        "id": tr.id,
        "asset_id": tr.asset_id,
        "asset_tag": tr.asset.asset_tag if tr.asset else None,
        "asset_name": tr.asset.name if tr.asset else None,
        "from_employee_name": _emp_name(tr.from_employee),
        "to_employee_name": _emp_name(tr.to_employee),
        "to_department_name": None,
        "requested_by_name": _emp_name(tr.requester),
        "reason": tr.reason,
        "status": tr.status,
        "approved_at": tr.approved_at,
        "created_at": tr.created_at,
    }


# ── Allocations ────────────────────────────────────────────────────────────────

@router.get("/", response_model=AllocationListResponse)
async def list_allocations(
    status_filter: Optional[str] = Query(None, alias="status"),
    overdue_only: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Employees see only their own; managers see all
    role = await user_repo.get_user_role_name(db, current_user.id)
    emp_filter = None
    if role == "employee":
        emp = await employee_repo.get_by_user_id(db, current_user.id)
        emp_filter = emp.id if emp else None

    skip = (page - 1) * page_size
    allocs, total = await allocation_repo.list_allocations(
        db,
        employee_id=emp_filter,
        status=status_filter,
        overdue_only=overdue_only,
        skip=skip,
        limit=page_size,
    )
    pages = (total + page_size - 1) // page_size if total > 0 else 0
    return AllocationListResponse(
        items=[_build_alloc(a) for a in allocs],
        total=total, page=page, page_size=page_size, pages=pages,
    )


@router.post("/", response_model=AllocationResponse, status_code=status.HTTP_201_CREATED)
async def allocate_asset(
    payload: AllocationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_manager(db, current_user)
    caller_emp = await _get_caller_employee(db, current_user)

    async with db.begin_nested():
        alloc = await allocation_service.allocate(
            db,
            asset_id=payload.asset_id,
            allocator_employee_id=caller_emp.id,
            to_employee_id=payload.allocated_to_employee_id,
            to_department_id=payload.allocated_to_department_id,
            expected_return_date=payload.expected_return_date,
        )
    await db.commit()
    alloc_full = await allocation_repo.get_by_id_with_relations(db, alloc.id)
    return _build_alloc(alloc_full)


@router.post("/{id}/return", response_model=AllocationResponse)
async def return_asset(
    id: UUID,
    payload: ReturnRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_manager(db, current_user)
    caller_emp = await _get_caller_employee(db, current_user)

    async with db.begin_nested():
        alloc = await allocation_service.return_asset(
            db,
            allocation_id=id,
            returned_by_employee_id=caller_emp.id,
            return_condition=payload.return_condition,
            return_notes=payload.return_notes,
        )
    await db.commit()
    alloc_full = await allocation_repo.get_by_id_with_relations(db, alloc.id)
    return _build_alloc(alloc_full)


@router.post("/{id}/transfer-request", response_model=TransferResponse, status_code=status.HTTP_201_CREATED)
async def create_transfer_request(
    id: UUID,
    payload: TransferRequestCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    caller_emp = await _get_caller_employee(db, current_user)
    if not payload.to_employee_id:
        raise HTTPException(status_code=400, detail="to_employee_id is required for transfer request.")

    # Get the allocation to find the asset
    alloc = await allocation_repo.get_by_id_with_relations(db, id)
    if not alloc:
        raise HTTPException(status_code=404, detail="Allocation not found.")

    async with db.begin_nested():
        tr = await allocation_service.create_transfer_request(
            db,
            asset_id=alloc.asset_id,
            requester_employee_id=caller_emp.id,
            to_employee_id=payload.to_employee_id,
            reason=payload.reason,
        )
    await db.commit()
    tr_full = await transfer_repo.get_by_id_with_relations(db, tr.id)
    return _build_transfer(tr_full)


# ── Transfers ──────────────────────────────────────────────────────────────────

@router.get("/transfers", response_model=TransferListResponse)
async def list_transfers(
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    skip = (page - 1) * page_size
    transfers, total = await transfer_repo.list_transfers(db, status=status_filter, skip=skip, limit=page_size)
    pages = (total + page_size - 1) // page_size if total > 0 else 0
    return TransferListResponse(
        items=[_build_transfer(t) for t in transfers],
        total=total, page=page, page_size=page_size, pages=pages,
    )


@router.post("/transfers/{transfer_id}/approve", response_model=TransferResponse)
async def approve_transfer(
    transfer_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_manager(db, current_user)
    caller_emp = await _get_caller_employee(db, current_user)

    async with db.begin_nested():
        tr = await allocation_service.approve_transfer(
            db, transfer_id=transfer_id, approver_employee_id=caller_emp.id
        )
    await db.commit()
    tr_full = await transfer_repo.get_by_id_with_relations(db, tr.id)
    return _build_transfer(tr_full)


@router.post("/transfers/{transfer_id}/reject", response_model=TransferResponse)
async def reject_transfer(
    transfer_id: UUID,
    payload: TransferActionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_manager(db, current_user)
    caller_emp = await _get_caller_employee(db, current_user)

    async with db.begin_nested():
        tr = await allocation_service.reject_transfer(
            db,
            transfer_id=transfer_id,
            approver_employee_id=caller_emp.id,
            rejection_reason=payload.rejection_reason,
        )
    await db.commit()
    tr_full = await transfer_repo.get_by_id_with_relations(db, tr.id)
    return _build_transfer(tr_full)
