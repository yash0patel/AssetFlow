from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.repositories.audit_repository import audit_repo
from app.repositories.user_repository import user_repo
from app.repositories.employee_repository import employee_repo
from app.schemas.audit import (
    AuditCycleCreate, AuditItemVerify, AuditCycleResponse, AuditItemResponse, AuditListResponse,
)
from app.services.audit_service import audit_service

router = APIRouter()


async def _require_admin(db, user):
    role = await user_repo.get_user_role_name(db, user.id)
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")


async def _require_auditor_or_admin(db, user):
    role = await user_repo.get_user_role_name(db, user.id)
    if role not in ("admin", "asset_manager", "department_head"):
        raise HTTPException(status_code=403, detail="Auditor or Admin access required.")


async def _get_emp(db, user):
    emp = await employee_repo.get_by_user_id(db, user.id)
    if not emp:
        raise HTTPException(status_code=403, detail="Must be an employee.")
    return emp


def _emp_name(emp):
    if emp and emp.user and emp.user.profile:
        p = emp.user.profile
        return f"{p.first_name} {p.last_name or ''}".strip()
    return None


def _build_cycle(cycle) -> dict:
    verified = sum(1 for i in cycle.items if i.verification_status == "Verified")
    discrepancies = sum(1 for i in cycle.items if i.verification_status in ("Missing", "Damaged"))
    return {
        "id": cycle.id,
        "cycle_name": cycle.cycle_name,
        "start_date": cycle.start_date,
        "end_date": cycle.end_date,
        "status": cycle.status,
        "scope_department_name": cycle.scope_department.name if cycle.scope_department else None,
        "scope_location_name": cycle.scope_location.name if cycle.scope_location else None,
        "creator_name": _emp_name(cycle.creator),
        "auditor_count": len(cycle.auditors),
        "item_count": len(cycle.items),
        "verified_count": verified,
        "discrepancy_count": discrepancies,
        "created_at": cycle.created_at,
    }


def _build_item(item) -> dict:
    return {
        "id": item.id,
        "audit_cycle_id": item.audit_cycle_id,
        "asset_id": item.asset_id,
        "asset_tag": item.asset.asset_tag if item.asset else None,
        "asset_name": item.asset.name if item.asset else None,
        "verification_status": item.verification_status,
        "verified_by_name": _emp_name(item.verifier) if hasattr(item, "verifier") else None,
        "verified_at": item.verified_at,
        "remarks": item.remarks,
    }


@router.get("/", response_model=AuditListResponse)
async def list_cycles(
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    skip = (page - 1) * page_size
    cycles, total = await audit_repo.list_cycles(db, status=status_filter, skip=skip, limit=page_size)
    pages = (total + page_size - 1) // page_size if total > 0 else 0
    return AuditListResponse(
        items=[_build_cycle(c) for c in cycles],
        total=total, page=page, page_size=page_size, pages=pages,
    )


@router.post("/", response_model=AuditCycleResponse, status_code=status.HTTP_201_CREATED)
async def create_cycle(
    payload: AuditCycleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_admin(db, current_user)
    emp = await _get_emp(db, current_user)
    async with db.begin_nested():
        cycle = await audit_service.create_cycle(
            db,
            cycle_name=payload.cycle_name,
            start_date=payload.start_date,
            end_date=payload.end_date,
            creator_employee_id=emp.id,
            scope_department_id=payload.scope_department_id,
            scope_location_id=payload.scope_location_id,
            auditor_ids=payload.auditor_ids,
        )
    await db.commit()
    cycle_full = await audit_repo.get_by_id_with_relations(db, cycle.id)
    return _build_cycle(cycle_full)


@router.get("/{id}", response_model=AuditCycleResponse)
async def get_cycle(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cycle = await audit_repo.get_by_id_with_relations(db, id)
    if not cycle:
        raise HTTPException(status_code=404, detail="Audit cycle not found.")
    return _build_cycle(cycle)


@router.get("/{id}/items", response_model=List[AuditItemResponse])
async def get_cycle_items(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = await audit_repo.get_items(db, id)
    return [_build_item(i) for i in items]


@router.post("/{id}/items/{item_id}/verify", response_model=AuditItemResponse)
async def verify_item(
    id: UUID,
    item_id: int,
    payload: AuditItemVerify,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_auditor_or_admin(db, current_user)
    emp = await _get_emp(db, current_user)
    async with db.begin_nested():
        item = await audit_service.verify_item(
            db,
            item_id=item_id,
            verifier_employee_id=emp.id,
            verification_status=payload.verification_status,
            remarks=payload.remarks,
        )
    await db.commit()
    item_full = await audit_repo.get_item(db, item_id)
    return _build_item(item_full)


@router.post("/{id}/close", response_model=AuditCycleResponse)
async def close_cycle(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_admin(db, current_user)
    emp = await _get_emp(db, current_user)
    async with db.begin_nested():
        cycle = await audit_service.close_cycle(db, cycle_id=id, closer_employee_id=emp.id)
    await db.commit()
    cycle_full = await audit_repo.get_by_id_with_relations(db, cycle.id)
    return _build_cycle(cycle_full)
