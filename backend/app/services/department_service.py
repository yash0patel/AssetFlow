from typing import List, Optional, Tuple
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.department import Department
from app.models.employee import Employee
from app.models.asset import Asset
from app.repositories.department_repository import department_repo
from app.repositories.employee_repository import employee_repo
from app.schemas.department import DepartmentCreate, DepartmentUpdate
from app.utils.helpers import utcnow

class DepartmentService:
    async def create(
        self, db: AsyncSession, *, obj_in: DepartmentCreate, creator_id: UUID
    ) -> Department:
        """Create a new department after validating business rules."""
        # 1. Prevent duplicate name
        existing_name = await department_repo.get_by_name(db, obj_in.name)
        if existing_name and existing_name.deleted_at is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Department with name '{obj_in.name}' already exists."
            )

        # 2. Prevent duplicate code
        if obj_in.code:
            existing_code = await department_repo.get_by_code(db, obj_in.code)
            if existing_code and existing_code.deleted_at is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Department with code '{obj_in.code}' already exists."
                )

        # 3. Validate parent department
        if obj_in.parent_department_id:
            parent = await department_repo.get(db, obj_in.parent_department_id)
            if not parent or parent.deleted_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent department does not exist."
                )
            if parent.status != "Active":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent department is inactive. Inactive departments cannot have children."
                )

        # Create
        dept = Department(
            name=obj_in.name,
            code=obj_in.code,
            parent_department_id=obj_in.parent_department_id,
            primary_location_id=obj_in.primary_location_id,
            status=obj_in.status,
            created_by=creator_id
        )
        await department_repo.create(db, obj_in=dept)
        
        # Build closure table hierarchy paths
        await department_repo.build_closure_for_new_dept(db, dept.id, dept.parent_department_id)
        
        return dept

    async def update(
        self, db: AsyncSession, *, id: UUID, obj_in: DepartmentUpdate
    ) -> Department:
        """Update a department after validating hierarchy loops and business rules."""
        dept = await department_repo.get(db, id)
        if not dept or dept.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found."
            )

        # Name duplicate check
        if obj_in.name and obj_in.name != dept.name:
            existing_name = await department_repo.get_by_name(db, obj_in.name)
            if existing_name and existing_name.deleted_at is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Department with name '{obj_in.name}' already exists."
                )
            dept.name = obj_in.name

        # Code duplicate check
        if obj_in.code and obj_in.code != dept.code:
            existing_code = await department_repo.get_by_code(db, obj_in.code)
            if existing_code and existing_code.deleted_at is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Department with code '{obj_in.code}' already exists."
                )
            dept.code = obj_in.code

        # Parent department hierarchy check
        if obj_in.parent_department_id is not None and obj_in.parent_department_id != dept.parent_department_id:
            parent = await department_repo.get(db, obj_in.parent_department_id)
            if not parent or parent.deleted_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent department does not exist."
                )
            if parent.status != "Active":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent department is inactive."
                )
            
            # Check for loops
            is_loop = await department_repo.check_hierarchy_loop(db, id, obj_in.parent_department_id)
            if is_loop:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid hierarchy: A department cannot be a child of itself or one of its descendants."
                )
            
            # Update parent relationship and rebuild closure paths
            dept.parent_department_id = obj_in.parent_department_id
            await department_repo.update_closure_for_parent_change(db, id, obj_in.parent_department_id)

        # Department head validation
        if obj_in.head_employee_id is not None and obj_in.head_employee_id != dept.head_employee_id:
            emp = await employee_repo.get(db, obj_in.head_employee_id)
            if not emp or emp.deleted_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Head employee does not exist."
                )
            if emp.status != "Active":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Head employee must be active."
                )
            if emp.department_id != id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Department Head must belong to the assigned department."
                )
            dept.head_employee_id = obj_in.head_employee_id

        # Update other fields
        if obj_in.primary_location_id is not None:
            dept.primary_location_id = obj_in.primary_location_id
        if obj_in.status is not None:
            dept.status = obj_in.status
            
        dept.updated_at = utcnow()
        await db.flush()
        return dept

    async def delete(self, db: AsyncSession, *, id: UUID) -> Department:
        """Soft delete a department after verifying it's not referenced by assets or employees."""
        dept = await department_repo.get(db, id)
        if not dept or dept.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found."
            )

        # 1. Prevent deletion if employees are assigned to it
        emp_stmt = select(Employee).where(and_(Employee.department_id == id, Employee.deleted_at.is_(None))).limit(1)
        emp_res = await db.execute(emp_stmt)
        if emp_res.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete department because active employees are assigned to it."
            )

        # 2. Prevent deletion if assets are assigned to it
        asset_stmt = select(Asset).where(and_(Asset.owning_department_id == id, Asset.deleted_at.is_(None))).limit(1)
        asset_res = await db.execute(asset_stmt)
        if asset_res.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete department because assets are assigned to it."
            )

        # 3. Soft delete
        dept.deleted_at = utcnow()
        await db.flush()
        return dept

department_service = DepartmentService()
