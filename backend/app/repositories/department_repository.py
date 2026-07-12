from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select, and_, or_, delete, insert, update, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.department import Department, DepartmentClosure
from app.models.employee import Employee
from app.models.user import User, UserProfile
from app.repositories.base_repository import BaseRepository

class DepartmentRepository(BaseRepository[Department]):
    def __init__(self):
        super().__init__(Department)

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Department]:
        """Fetch department by name (case-insensitive)."""
        stmt = select(Department).where(text("lower(name) = :name")).params(name=name.lower())
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_code(self, db: AsyncSession, code: str) -> Optional[Department]:
        """Fetch department by short code (case-insensitive)."""
        stmt = select(Department).where(text("lower(code) = :code")).params(code=code.lower())
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_departments(
        self,
        db: AsyncSession,
        *,
        search: Optional[str] = None,
        status: Optional[str] = None,
        parent_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "name",
        sort_order: str = "asc"
    ) -> Tuple[List[Department], int]:
        """List departments with pagination, searching, filtering, and sorting."""
        stmt = select(Department).where(Department.deleted_at.is_(None))

        # Filters
        if search:
            stmt = stmt.where(
                or_(
                    Department.name.ilike(f"%{search}%"),
                    Department.code.ilike(f"%{search}%")
                )
            )
        if status:
            stmt = stmt.where(Department.status == status)
        if parent_id is not None:
            stmt = stmt.where(Department.parent_department_id == parent_id)

        # Count total
        count_stmt = select(text("count(*)")).select_from(stmt.subquery())
        total_res = await db.execute(count_stmt)
        total = total_res.scalar_one()

        # Eager load parent and department head details
        stmt = stmt.options(
            selectinload(Department.parent_department),
            selectinload(Department.head_employee).selectinload(Employee.user).selectinload(User.profile)
        )

        # Sorting
        sort_attr = getattr(Department, sort_by, Department.name)
        if sort_order.lower() == "desc":
            stmt = stmt.order_by(sort_attr.desc())
        else:
            stmt = stmt.order_by(sort_attr.asc())

        # Pagination
        stmt = stmt.offset(skip).limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars().all()), total

    async def check_hierarchy_loop(
        self, db: AsyncSession, department_id: UUID, new_parent_id: UUID
    ) -> bool:
        """
        Check if making new_parent_id the parent of department_id creates a cycle.
        Returns True if a cycle would be created (i.e. new_parent_id is department_id or is a descendant of department_id).
        """
        if department_id == new_parent_id:
            return True

        # Query closure table to see if a path exists from department_id (ancestor) to new_parent_id (descendant)
        stmt = select(DepartmentClosure).where(
            and_(
                DepartmentClosure.ancestor_id == department_id,
                DepartmentClosure.descendant_id == new_parent_id
            )
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none() is not None

    async def build_closure_for_new_dept(
        self, db: AsyncSession, department_id: UUID, parent_id: Optional[UUID]
    ) -> None:
        """Initialize closure table paths for a newly created department."""
        # 1. Insert self path (depth 0)
        db.add(DepartmentClosure(ancestor_id=department_id, descendant_id=department_id, depth=0))
        
        # 2. If parent exists, copy all parent's ancestor paths incremented by 1 depth
        if parent_id:
            stmt = select(DepartmentClosure).where(DepartmentClosure.descendant_id == parent_id)
            res = await db.execute(stmt)
            for path in res.scalars().all():
                db.add(
                    DepartmentClosure(
                        ancestor_id=path.ancestor_id,
                        descendant_id=department_id,
                        depth=path.depth + 1
                    )
                )
        await db.flush()

    async def update_closure_for_parent_change(
        self, db: AsyncSession, department_id: UUID, new_parent_id: Optional[UUID]
    ) -> None:
        """
        Rebuilds closure paths when a department's parent is changed.
        """
        # Step 1: Disconnect department_id (and all its descendants) from all department_id's old strict ancestors.
        # Strict ancestors of D are ancestors where descendant is D and depth > 0.
        # Descendants of D are descendants in closure where ancestor is D.
        
        # Fetch all descendants of D (including D itself)
        desc_stmt = select(DepartmentClosure.descendant_id).where(
            DepartmentClosure.ancestor_id == department_id
        )
        desc_res = await db.execute(desc_stmt)
        descendant_ids = list(desc_res.scalars().all())

        # Fetch all strict ancestors of D (excluding D itself)
        anc_stmt = select(DepartmentClosure.ancestor_id).where(
            and_(
                DepartmentClosure.descendant_id == department_id,
                DepartmentClosure.depth > 0
            )
        )
        anc_res = await db.execute(anc_stmt)
        ancestor_ids = list(anc_res.scalars().all())

        if ancestor_ids and descendant_ids:
            # Delete paths from D's strict ancestors to D's descendants
            del_stmt = delete(DepartmentClosure).where(
                and_(
                    DepartmentClosure.ancestor_id.in_(ancestor_ids),
                    DepartmentClosure.descendant_id.in_(descendant_ids)
                )
            )
            await db.execute(del_stmt)

        # Step 2: Connect all descendants of D to all ancestors of the new parent.
        if new_parent_id:
            # Fetch new ancestors of the parent (including the parent itself)
            new_anc_stmt = select(DepartmentClosure.ancestor_id, DepartmentClosure.depth).where(
                DepartmentClosure.descendant_id == new_parent_id
            )
            new_anc_res = await db.execute(new_anc_stmt)
            new_ancestors = new_anc_res.all()  # list of tuples (ancestor_id, depth)

            # Fetch descendant depths relative to D
            rel_desc_stmt = select(DepartmentClosure.descendant_id, DepartmentClosure.depth).where(
                DepartmentClosure.ancestor_id == department_id
            )
            rel_desc_res = await db.execute(rel_desc_stmt)
            rel_descendants = rel_desc_res.all()  # list of tuples (descendant_id, depth)

            for anc_id, anc_depth in new_ancestors:
                for desc_id, desc_depth in rel_descendants:
                    db.add(
                        DepartmentClosure(
                            ancestor_id=anc_id,
                            descendant_id=desc_id,
                            depth=anc_depth + desc_depth + 1
                        )
                    )
        await db.flush()

department_repo = DepartmentRepository()
