from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy import select, or_, and_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.employee import Employee
from app.models.user import User, UserProfile, UserRole, Role
from app.models.department import Department
from app.repositories.base_repository import BaseRepository

class EmployeeRepository(BaseRepository[Employee]):
    def __init__(self):
        super().__init__(Employee)

    async def get_by_user_id(self, db: AsyncSession, user_id: UUID) -> Optional[Employee]:
        """Fetch employee by associated user ID."""
        stmt = (
            select(Employee)
            .where(Employee.user_id == user_id)
            .options(
                selectinload(Employee.user).selectinload(User.profile),
                selectinload(Employee.department)
            )
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_employee_code(self, db: AsyncSession, employee_code: str) -> Optional[Employee]:
        """Fetch employee by employee code."""
        stmt = select(Employee).where(Employee.employee_code == employee_code)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_id_with_relations(self, db: AsyncSession, employee_id: UUID) -> Optional[Employee]:
        """Fetch single employee eagerly loading user, profile, department, and reporting manager."""
        stmt = (
            select(Employee)
            .where(Employee.id == employee_id)
            .options(
                selectinload(Employee.user).selectinload(User.profile),
                selectinload(Employee.department),
                selectinload(Employee.reporting_manager)
            )
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_employees(
        self,
        db: AsyncSession,
        *,
        search: Optional[str] = None,
        department_id: Optional[UUID] = None,
        reporting_manager_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "name",
        sort_order: str = "asc"
    ) -> Tuple[List[Employee], int]:
        """List employees with pagination, searching, filtering, and sorting."""
        # Start statement
        stmt = select(Employee).join(User, Employee.user_id == User.id).outerjoin(UserProfile, User.id == UserProfile.user_id)

        # Filters
        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Employee.employee_code.ilike(search_pattern),
                    UserProfile.first_name.ilike(search_pattern),
                    UserProfile.last_name.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                    Employee.designation.ilike(search_pattern)
                )
            )
        if department_id is not None:
            stmt = stmt.where(Employee.department_id == department_id)
        if reporting_manager_id is not None:
            stmt = stmt.where(Employee.reporting_manager_id == reporting_manager_id)
        if status:
            stmt = stmt.where(Employee.status == status)

        # Count total
        count_stmt = select(text("count(*)")).select_from(stmt.subquery())
        total_res = await db.execute(count_stmt)
        total = total_res.scalar_one()

        # Eager load relationships
        stmt = stmt.options(
            selectinload(Employee.user).selectinload(User.profile),
            selectinload(Employee.user).selectinload(User.user_roles).selectinload(UserRole.role),
            selectinload(Employee.department),
            selectinload(Employee.reporting_manager).selectinload(Employee.user).selectinload(User.profile)
        )

        # Sorting
        if sort_by == "name":
            sort_attr = UserProfile.first_name
        elif sort_by == "email":
            sort_attr = User.email
        elif sort_by == "employee_code":
            sort_attr = Employee.employee_code
        else:
            sort_attr = getattr(Employee, sort_by, Employee.created_at)

        if sort_order.lower() == "desc":
            stmt = stmt.order_by(sort_attr.desc())
        else:
            stmt = stmt.order_by(sort_attr.asc())

        # Pagination
        stmt = stmt.offset(skip).limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars().all()), total

    async def get_users_without_employee(self, db: AsyncSession) -> List[User]:
        """Fetch users who do not have an employee record yet."""
        stmt = (
            select(User)
            .outerjoin(Employee, Employee.user_id == User.id)
            .where(Employee.id.is_(None))
            .options(selectinload(User.profile))
            .order_by(User.email)
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

employee_repo = EmployeeRepository()
