from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_current_user, get_db
from app.models.user import User, UserRole
from app.models.employee import Employee
from app.repositories.user_repository import user_repo
from app.repositories.employee_repository import employee_repo
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeListResponse,
    EmployeeResponse,
    EmployeeUpdate,
    RolePromotionRequest,
    UserWithoutEmployeeResponse,
)
from app.services.employee_service import employee_service

router = APIRouter()

async def require_admin(db: AsyncSession, user: User) -> None:
    role_name = await user_repo.get_user_role_name(db, user.id)
    if role_name not in ("admin", "super_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Administrator privileges required."
        )

async def require_admin_or_manager(db: AsyncSession, user: User) -> None:
    role_name = await user_repo.get_user_role_name(db, user.id)
    if role_name not in ("admin", "super_admin", "manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Manager or Administrator privileges required."
        )

def get_employee_display_role(user: User) -> str:
    """Determine the employee's display role based on active DB roles and scopes."""
    active_roles = [ur for ur in user.user_roles if ur.revoked_at is None]
    
    # 1. Admin
    for ur in active_roles:
        if ur.role.name in ("admin", "super_admin"):
            return "Admin"
            
    # 2. Manager
    for ur in active_roles:
        if ur.role.name == "manager":
            if ur.department_scope_id is not None:
                return "Department Head"
            else:
                return "Asset Manager"
                
    return "Employee"

def build_employee_response(emp: Employee) -> dict:
    """Helper to convert Employee model to response dict."""
    profile = emp.user.profile
    first_name = profile.first_name if profile else ""
    last_name = profile.last_name if profile else None
    name = f"{first_name} {last_name}".strip() if last_name else first_name

    rep_mgr_name = None
    if emp.reporting_manager and emp.reporting_manager.user.profile:
        m_prof = emp.reporting_manager.user.profile
        m_last = m_prof.last_name or ""
        rep_mgr_name = f"{m_prof.first_name} {m_last}".strip()

    return {
        "id": emp.id,
        "user_id": emp.user_id,
        "employee_code": emp.employee_code,
        "department_id": emp.department_id,
        "designation": emp.designation,
        "reporting_manager_id": emp.reporting_manager_id,
        "date_of_joining": emp.date_of_joining,
        "status": emp.status,
        "created_at": emp.created_at,
        "updated_at": emp.updated_at,
        "name": name or emp.user.email,
        "email": emp.user.email,
        "department_name": emp.department.name if emp.department else None,
        "reporting_manager_name": rep_mgr_name,
        "role": get_employee_display_role(emp.user)
    }

@router.get("/", response_model=EmployeeListResponse)
async def list_employees(
    search: Optional[str] = Query(None, description="Search by name, email, designation, or code"),
    department_id: Optional[UUID] = Query(None, description="Filter by department ID"),
    reporting_manager_id: Optional[UUID] = Query(None, description="Filter by reporting manager ID"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (Active/Inactive)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    sort_by: str = Query("name"),
    sort_order: str = Query("asc"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch complete list of employees with search and pagination details."""
    await require_admin_or_manager(db, current_user)
    
    skip = (page - 1) * page_size
    employees, total = await employee_repo.list_employees(
        db,
        search=search,
        department_id=department_id,
        reporting_manager_id=reporting_manager_id,
        status=status_filter,
        skip=skip,
        limit=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )

    items = [build_employee_response(e) for e in employees]
    pages = (total + page_size - 1) // page_size if total > 0 else 0

    return EmployeeListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )

@router.get("/users-without-employee", response_model=List[UserWithoutEmployeeResponse])
async def list_users_without_employee(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch a list of registered users who do not have an Employee record yet."""
    await require_admin_or_manager(db, current_user)
    users = await employee_repo.get_users_without_employee(db)
    
    resp = []
    for u in users:
        first_name = u.profile.first_name if u.profile else ""
        last_name = u.profile.last_name if u.profile else ""
        name = f"{first_name} {last_name}".strip()
        resp.append({
            "id": u.id,
            "email": u.email,
            "name": name or u.email
        })
    return resp

@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    payload: EmployeeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new employee record linked to a user account."""
    await require_admin(db, current_user)
    
    async with db.begin_nested():
        emp = await employee_service.create(db, obj_in=payload)
    await db.commit()
    
    db_emp = await employee_repo.get_by_id_with_relations(db, emp.id)
    return build_employee_response(db_emp or emp)

@router.get("/{id}", response_model=EmployeeResponse)
async def get_employee(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch full employee profile details."""
    await require_admin_or_manager(db, current_user)
    
    emp = await employee_repo.get_by_id_with_relations(db, id)
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found.")
    return build_employee_response(emp)

@router.put("/{id}", response_model=EmployeeResponse)
async def update_employee(
    id: UUID,
    payload: EmployeeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update details of an employee record."""
    await require_admin(db, current_user)
    
    async with db.begin_nested():
        emp = await employee_service.update(db, id=id, obj_in=payload)
    await db.commit()

    db_emp = await employee_repo.get_by_id_with_relations(db, id)
    return build_employee_response(db_emp or emp)

@router.post("/{id}/promote", status_code=status.HTTP_200_OK)
async def promote_employee(
    id: UUID,
    payload: RolePromotionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Promote an employee to Department Head or Asset Manager."""
    await require_admin(db, current_user)
    
    # Prevent self-escalation
    emp = await employee_repo.get(db, id)
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found.")
        
    if current_user.id == emp.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Self role promotion is forbidden. Admins cannot promote themselves."
        )

    async with db.begin_nested():
        await employee_service.promote(
            db,
            employee_id=id,
            target_role=payload.role,
            department_scope_id=payload.department_scope_id,
            admin_id=current_user.id
        )
    await db.commit()
    
    return {"detail": f"Successfully promoted to {payload.role}."}

@router.post("/{id}/demote", status_code=status.HTTP_200_OK)
async def demote_employee(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke all promoted roles and demote user back to standard Employee."""
    await require_admin(db, current_user)
    
    emp = await employee_repo.get(db, id)
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found.")
        
    if current_user.id == emp.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Self role demotion is forbidden. Admins cannot demote themselves."
        )

    async with db.begin_nested():
        await employee_service.demote(db, employee_id=id)
    await db.commit()
    
    return {"detail": "Successfully demoted employee."}
