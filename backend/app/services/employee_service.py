from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_

from app.models.employee import Employee
from app.models.user import User, UserRole, Role
from app.models.department import Department
from app.db.sequence import get_next_sequence_value
from app.repositories.employee_repository import employee_repo
from app.repositories.department_repository import department_repo
from app.repositories.user_repository import user_repo
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.utils.helpers import utcnow

class EmployeeService:
    async def create(
        self, db: AsyncSession, *, obj_in: EmployeeCreate
    ) -> Employee:
        """Create a new employee and link it to a user."""
        # 1. Check user exists
        user = await user_repo.get_by_id(db, obj_in.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User account not found."
            )

        # 2. Check employee doesn't already exist for user
        existing = await employee_repo.get_by_user_id(db, obj_in.user_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An employee record is already linked to this user."
            )

        # 3. Validate department status
        if obj_in.department_id:
            dept = await department_repo.get(db, obj_in.department_id)
            if not dept or dept.deleted_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Department does not exist."
                )
            if dept.status != "Active":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Inactive departments cannot receive new employees."
                )

        # 4. Validate manager
        if obj_in.reporting_manager_id:
            mgr = await employee_repo.get(db, obj_in.reporting_manager_id)
            if not mgr or mgr.deleted_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Reporting manager does not exist."
                )
            if mgr.status != "Active":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Reporting manager must be active."
                )

        # Generate Employee Code
        employee_code = await get_next_sequence_value(db, "EMP")

        # Create
        emp = Employee(
            user_id=obj_in.user_id,
            employee_code=employee_code,
            department_id=obj_in.department_id,
            designation=obj_in.designation,
            reporting_manager_id=obj_in.reporting_manager_id,
            date_of_joining=obj_in.date_of_joining,
            status=obj_in.status
        )
        await employee_repo.create(db, obj_in=emp)
        return emp

    async def update(
        self, db: AsyncSession, *, id: UUID, obj_in: EmployeeUpdate
    ) -> Employee:
        """Update employee directory placement and reporting structure."""
        emp = await employee_repo.get(db, id)
        if not emp or emp.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee record not found."
            )

        # Department validation
        if obj_in.department_id is not None and obj_in.department_id != emp.department_id:
            dept = await department_repo.get(db, obj_in.department_id)
            if not dept or dept.deleted_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Department does not exist."
                )
            if dept.status != "Active":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Inactive departments cannot receive new employees."
                )

            # If they were Department Head of their old department, clear it!
            old_dept_stmt = select(Department).where(Department.head_employee_id == id)
            old_dept_res = await db.execute(old_dept_stmt)
            for old_dept in old_dept_res.scalars().all():
                old_dept.head_employee_id = None

            emp.department_id = obj_in.department_id

        # Reporting manager validation
        if obj_in.reporting_manager_id is not None and obj_in.reporting_manager_id != emp.reporting_manager_id:
            if obj_in.reporting_manager_id == id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="An employee cannot report to themselves."
                )
            
            mgr = await employee_repo.get(db, obj_in.reporting_manager_id)
            if not mgr or mgr.deleted_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Reporting manager does not exist."
                )
            if mgr.status != "Active":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Reporting manager must be active."
                )

            # Cycle check
            if await self._has_manager_loop(db, id, obj_in.reporting_manager_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Reporting loop detected: Manager chain cannot cycle back to employee."
                )
            
            emp.reporting_manager_id = obj_in.reporting_manager_id

        # Status change
        if obj_in.status is not None and obj_in.status != emp.status:
            if obj_in.status == "Inactive":
                # Clear them from heading any department
                heading_dept_stmt = select(Department).where(Department.head_employee_id == id)
                heading_dept_res = await db.execute(heading_dept_stmt)
                for heading_dept in heading_dept_res.scalars().all():
                    heading_dept.head_employee_id = None
            emp.status = obj_in.status

        # Other fields
        if obj_in.designation is not None:
            emp.designation = obj_in.designation
        if obj_in.date_of_joining is not None:
            emp.date_of_joining = obj_in.date_of_joining

        emp.updated_at = utcnow()
        await db.flush()
        return emp

    async def promote(
        self, db: AsyncSession, *, employee_id: UUID, target_role: str, department_scope_id: Optional[UUID], admin_id: UUID
    ) -> None:
        """Promote an employee to a specialized role (Department Head or Asset Manager)."""
        emp = await employee_repo.get(db, employee_id)
        if not emp or emp.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee record not found."
            )

        if emp.status != "Active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot promote an inactive employee."
            )

        # Get role model for 'manager'
        stmt_role = select(Role).where(Role.name == "manager")
        res_role = await db.execute(stmt_role)
        manager_role = res_role.scalar_one_or_none()
        if not manager_role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database setup error: 'manager' role not found."
            )

        # Business Rules
        if target_role == "Department Head":
            if not department_scope_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Department scope is required to promote to Department Head."
                )
            if emp.department_id != department_scope_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Department Head must belong to their assigned department."
                )
            
            # Update the department table's head_employee_id
            dept = await department_repo.get(db, department_scope_id)
            if not dept or dept.deleted_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Department does not exist."
                )
            dept.head_employee_id = employee_id

        elif target_role == "Asset Manager":
            # Asset Manager is org-wide
            department_scope_id = None

        # Revoke any active manager role for the user first to avoid duplication
        stmt_revoke = (
            update(UserRole)
            .where(
                and_(
                    UserRole.user_id == emp.user_id,
                    UserRole.role_id == manager_role.id,
                    UserRole.revoked_at.is_(None)
                )
            )
            .values(revoked_at=utcnow())
        )
        await db.execute(stmt_revoke)

        # Add UserRole assignment
        user_role = UserRole(
            user_id=emp.user_id,
            role_id=manager_role.id,
            department_scope_id=department_scope_id,
            assigned_by=admin_id,
            assigned_at=utcnow()
        )
        db.add(user_role)
        await db.flush()

    async def demote(self, db: AsyncSession, *, employee_id: UUID) -> None:
        """Demote an employee by revoking their promoted roles and resetting to standard Employee."""
        emp = await employee_repo.get(db, employee_id)
        if not emp or emp.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee record not found."
            )

        # Find manager role
        stmt_role = select(Role).where(Role.name == "manager")
        res_role = await db.execute(stmt_role)
        manager_role = res_role.scalar_one_or_none()
        if not manager_role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database setup error: 'manager' role not found."
            )

        # Revoke the manager role
        stmt_revoke = (
            update(UserRole)
            .where(
                and_(
                    UserRole.user_id == emp.user_id,
                    UserRole.role_id == manager_role.id,
                    UserRole.revoked_at.is_(None)
                )
            )
            .values(revoked_at=utcnow())
        )
        await db.execute(stmt_revoke)

        # Clear department head reference if any
        dept_stmt = select(Department).where(Department.head_employee_id == employee_id)
        dept_res = await db.execute(dept_stmt)
        for dept in dept_res.scalars().all():
            dept.head_employee_id = None

        await db.flush()

    async def _has_manager_loop(self, db: AsyncSession, employee_id: UUID, manager_id: UUID) -> bool:
        """Detect reporting structure manager cycle loops."""
        current_id = manager_id
        visited = set()
        while current_id:
            if current_id == employee_id:
                return True
            if current_id in visited:
                break
            visited.add(current_id)
            mgr = await employee_repo.get(db, current_id)
            if not mgr:
                break
            current_id = mgr.reporting_manager_id
        return False

employee_service = EmployeeService()
