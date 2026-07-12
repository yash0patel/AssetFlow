from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.department import Department
from app.models.employee import Employee
from app.repositories.user_repository import user_repo
from app.repositories.department_repository import department_repo
from app.schemas.department import (
    DepartmentCreate,
    DepartmentListResponse,
    DepartmentResponse,
    DepartmentUpdate,
)
from app.services.department_service import department_service

router = APIRouter()

async def require_admin(db: AsyncSession, user: User) -> None:
    role_name = await user_repo.get_user_role_name(db, user.id)
    if role_name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Administrator privileges required."
        )

async def require_admin_or_manager(db: AsyncSession, user: User) -> None:
    role_name = await user_repo.get_user_role_name(db, user.id)
    if role_name not in ("admin", "asset_manager", "department_head"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Manager, Department Head, or Administrator privileges required."
        )

def build_response_dict(dept: Department) -> dict:
    """Helper to structure department details for schema validation."""
    parent_name = dept.parent_department.name if dept.parent_department else None
    head_name = ""
    if dept.head_employee and dept.head_employee.user.profile:
        prof = dept.head_employee.user.profile
        head_name = f"{prof.first_name} {prof.last_name or ''}".strip()
    return {
        "id": dept.id,
        "name": dept.name,
        "code": dept.code,
        "head_employee_id": dept.head_employee_id,
        "parent_department_id": dept.parent_department_id,
        "primary_location_id": dept.primary_location_id,
        "status": dept.status,
        "created_by": dept.created_by,
        "created_at": dept.created_at,
        "updated_at": dept.updated_at,
        "parent_name": parent_name,
        "head_name": head_name or None
    }

@router.get("/", response_model=DepartmentListResponse)
async def list_departments(
    search: Optional[str] = Query(None, description="Search term for department name or code"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (Active/Inactive)"),
    parent_id: Optional[UUID] = Query(None, description="Filter by parent department ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Page size"),
    sort_by: str = Query("name", description="Field to sort by"),
    sort_order: str = Query("asc", description="Sort order (asc/desc)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List departments with pagination, searching, filtering, and sorting."""
    await require_admin_or_manager(db, current_user)
    
    skip = (page - 1) * page_size
    depts, total = await department_repo.list_departments(
        db,
        search=search,
        status=status_filter,
        parent_id=parent_id,
        skip=skip,
        limit=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )

    items = [build_response_dict(d) for d in depts]
    pages = (total + page_size - 1) // page_size if total > 0 else 0

    return DepartmentListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )

@router.post("/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    payload: DepartmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new department."""
    await require_admin(db, current_user)
    async with db.begin_nested():
        dept = await department_service.create(db, obj_in=payload, creator_id=current_user.id)
    await db.commit()
    
    # Reload with relationships
    db_dept = await department_repo.get_departments_with_relations(db, dept.id)
    return build_response_dict(db_dept or dept)

@router.get("/{id}", response_model=DepartmentResponse)
async def get_department(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch details of a single department."""
    await require_admin_or_manager(db, current_user)
    
    # Simple query helper with eager loads
    stmt = (
        select(Department)
        .where(and_(Department.id == id, Department.deleted_at.is_(None)))
        .options(
            selectinload(Department.parent_department),
            selectinload(Department.head_employee).selectinload(Employee.user).selectinload(User.profile)
        )
    )
    res = await db.execute(stmt)
    dept = res.scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found.")
    
    return build_response_dict(dept)

@router.put("/{id}", response_model=DepartmentResponse)
async def update_department(
    id: UUID,
    payload: DepartmentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update details of a department."""
    await require_admin(db, current_user)
    
    async with db.begin_nested():
        dept = await department_service.update(db, id=id, obj_in=payload)
    await db.commit()

    # Reload with relationships
    stmt = (
        select(Department)
        .where(Department.id == id)
        .options(
            selectinload(Department.parent_department),
            selectinload(Department.head_employee).selectinload(Employee.user).selectinload(User.profile)
        )
    )
    res = await db.execute(stmt)
    db_dept = res.scalar_one_or_none()
    return build_response_dict(db_dept or dept)

@router.delete("/{id}", response_model=DepartmentResponse)
async def delete_department(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete a department."""
    await require_admin(db, current_user)
    
    async with db.begin_nested():
        dept = await department_service.delete(db, id=id)
    # Reload with relations before return to prevent lazy loading
    db_dept = await department_repo.get_departments_with_relations(db, id)
    return build_response_dict(db_dept or dept)

# Eager-load extension helper for reload
async def _get_dept_with_relations(self, db: AsyncSession, id: UUID) -> Optional[Department]:
    stmt = select(Department).where(Department.id == id).options(
        selectinload(Department.parent_department),
        selectinload(Department.head_employee).selectinload(Employee.user).selectinload(User.profile)
    )
    res = await db.execute(stmt)
    return res.scalar_one_or_none()

# Attach it to repo instance dynamically
department_repo.get_departments_with_relations = _get_dept_with_relations.__get__(department_repo, type(department_repo))
