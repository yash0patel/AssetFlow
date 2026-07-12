from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.repositories.maintenance_repository import maintenance_repo
from app.repositories.user_repository import user_repo
from app.repositories.employee_repository import employee_repo
from app.schemas.maintenance import (
    MaintenanceCreate, MaintenanceApprove, MaintenanceAssign, MaintenanceReject, MaintenanceResolve,
    MaintenanceResponse, MaintenanceListResponse, TechnicianResponse,
)
from app.services.maintenance_service import maintenance_service

router = APIRouter()


async def _get_emp(db, user):
    emp = await employee_repo.get_by_user_id(db, user.id)
    if not emp:
        raise HTTPException(status_code=403, detail="Must be an employee.")
    return emp


async def _require_manager(db, user):
    role = await user_repo.get_user_role_name(db, user.id)
    if role not in ("admin", "asset_manager"):
        raise HTTPException(status_code=403, detail="Asset Manager or Admin required.")


def _build(mr) -> dict:
    def emp_name(e):
        if e and e.user and e.user.profile:
            p = e.user.profile
            return f"{p.first_name} {p.last_name or ''}".strip()
        return None

    return {
        "id": mr.id,
        "request_code": mr.request_code,
        "asset_id": mr.asset_id,
        "asset_tag": mr.asset.asset_tag if mr.asset else None,
        "asset_name": mr.asset.name if mr.asset else None,
        "raised_by_name": emp_name(mr.raised_by_employee),
        "issue_description": mr.issue_description,
        "priority": mr.priority,
        "status": mr.status,
        "technician_id": mr.technician_id,
        "technician_name": mr.technician.name if mr.technician else None,
        "rejection_reason": mr.rejection_reason,
        "resolution_notes": mr.resolution_notes,
        "approved_at": mr.approved_at,
        "started_at": mr.started_at,
        "resolved_at": mr.resolved_at,
        "created_at": mr.created_at,
        "updated_at": mr.updated_at,
    }


@router.get("/technicians", response_model=List[TechnicianResponse])
async def list_technicians(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    techs = await maintenance_repo.list_technicians(db)
    return techs


@router.get("/", response_model=MaintenanceListResponse)
async def list_maintenance(
    status_filter: Optional[str] = Query(None, alias="status"),
    asset_id: Optional[UUID] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    role = await user_repo.get_user_role_name(db, current_user.id)
    emp_filter = None
    if role == "employee":
        emp = await employee_repo.get_by_user_id(db, current_user.id)
        emp_filter = emp.id if emp else None

    skip = (page - 1) * page_size
    items, total = await maintenance_repo.list_requests(
        db, asset_id=asset_id, status=status_filter, raised_by=emp_filter,
        skip=skip, limit=page_size,
    )
    pages = (total + page_size - 1) // page_size if total > 0 else 0
    return MaintenanceListResponse(
        items=[_build(m) for m in items],
        total=total, page=page, page_size=page_size, pages=pages,
    )


@router.post("/", response_model=MaintenanceResponse, status_code=status.HTTP_201_CREATED)
async def raise_maintenance(
    payload: MaintenanceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    emp = await _get_emp(db, current_user)
    async with db.begin_nested():
        mr = await maintenance_service.raise_request(
            db,
            asset_id=payload.asset_id,
            raised_by_employee_id=emp.id,
            issue_description=payload.issue_description,
            priority=payload.priority,
        )
    await db.commit()
    mr_full = await maintenance_repo.get_by_id_with_relations(db, mr.id)
    return _build(mr_full)


@router.get("/{id}", response_model=MaintenanceResponse)
async def get_maintenance(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    mr = await maintenance_repo.get_by_id_with_relations(db, id)
    if not mr:
        raise HTTPException(status_code=404, detail="Maintenance request not found.")
    return _build(mr)


@router.post("/{id}/approve", response_model=MaintenanceResponse)
async def approve_maintenance(
    id: UUID,
    payload: MaintenanceApprove,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_manager(db, current_user)
    emp = await _get_emp(db, current_user)
    async with db.begin_nested():
        mr = await maintenance_service.approve(
            db, mr_id=id, approver_employee_id=emp.id, technician_id=payload.technician_id
        )
    await db.commit()
    mr_full = await maintenance_repo.get_by_id_with_relations(db, mr.id)
    return _build(mr_full)


@router.post("/{id}/reject", response_model=MaintenanceResponse)
async def reject_maintenance(
    id: UUID,
    payload: MaintenanceReject,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_manager(db, current_user)
    emp = await _get_emp(db, current_user)
    async with db.begin_nested():
        mr = await maintenance_service.reject(
            db, mr_id=id, approver_employee_id=emp.id, rejection_reason=payload.rejection_reason
        )
    await db.commit()
    mr_full = await maintenance_repo.get_by_id_with_relations(db, mr.id)
    return _build(mr_full)


@router.post("/{id}/assign", response_model=MaintenanceResponse)
async def assign_technician(
    id: UUID,
    payload: MaintenanceAssign,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_manager(db, current_user)
    async with db.begin_nested():
        mr = await maintenance_service.assign_technician(
            db, mr_id=id, technician_id=payload.technician_id
        )
    await db.commit()
    mr_full = await maintenance_repo.get_by_id_with_relations(db, mr.id)
    return _build(mr_full)


@router.post("/{id}/start", response_model=MaintenanceResponse)
async def start_maintenance(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_manager(db, current_user)
    async with db.begin_nested():
        mr = await maintenance_service.start(db, mr_id=id)
    await db.commit()
    mr_full = await maintenance_repo.get_by_id_with_relations(db, mr.id)
    return _build(mr_full)


@router.post("/{id}/resolve", response_model=MaintenanceResponse)
async def resolve_maintenance(
    id: UUID,
    payload: MaintenanceResolve,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _require_manager(db, current_user)
    async with db.begin_nested():
        mr = await maintenance_service.resolve(
            db, mr_id=id, resolution_notes=payload.resolution_notes, actual_cost=payload.actual_cost
        )
    await db.commit()
    mr_full = await maintenance_repo.get_by_id_with_relations(db, mr.id)
    return _build(mr_full)
