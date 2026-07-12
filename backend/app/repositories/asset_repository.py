from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import select, or_, and_, text, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.asset import Asset, AssetStatusHistory, AssetLocation
from app.models.department import AssetCategory
from app.models.employee import Employee
from app.models.user import User, UserProfile
from app.repositories.base_repository import BaseRepository


class AssetRepository(BaseRepository[Asset]):
    def __init__(self):
        super().__init__(Asset)

    async def get_by_tag(self, db: AsyncSession, asset_tag: str) -> Optional[Asset]:
        stmt = select(Asset).where(Asset.asset_tag == asset_tag)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_id_with_relations(self, db: AsyncSession, asset_id: UUID) -> Optional[Asset]:
        stmt = (
            select(Asset)
            .where(Asset.id == asset_id, Asset.deleted_at.is_(None))
            .options(
                selectinload(Asset.category),
                selectinload(Asset.current_location),
                selectinload(Asset.owning_department),
                selectinload(Asset.current_holder_employee).selectinload(Employee.user).selectinload(User.profile),
                selectinload(Asset.created_by_user).selectinload(User.profile),
                selectinload(Asset.status_history),
                selectinload(Asset.custom_attribute_values),
            )
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_assets(
        self,
        db: AsyncSession,
        *,
        search: Optional[str] = None,
        category_id: Optional[UUID] = None,
        status: Optional[str] = None,
        department_id: Optional[UUID] = None,
        location_id: Optional[UUID] = None,
        is_bookable: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> Tuple[List[Asset], int]:
        stmt = select(Asset).where(Asset.deleted_at.is_(None))

        if search:
            q = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Asset.asset_tag.ilike(q),
                    Asset.name.ilike(q),
                    Asset.serial_number.ilike(q),
                    Asset.qr_code_value.ilike(q),
                )
            )
        if category_id:
            stmt = stmt.where(Asset.category_id == category_id)
        if status:
            stmt = stmt.where(Asset.current_status == status)
        if department_id:
            stmt = stmt.where(Asset.owning_department_id == department_id)
        if location_id:
            stmt = stmt.where(Asset.current_location_id == location_id)
        if is_bookable is not None:
            stmt = stmt.where(Asset.is_bookable == is_bookable)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_res = await db.execute(count_stmt)
        total = total_res.scalar_one()

        stmt = stmt.options(
            selectinload(Asset.category),
            selectinload(Asset.current_location),
            selectinload(Asset.owning_department),
            selectinload(Asset.current_holder_employee).selectinload(Employee.user).selectinload(User.profile),
        )

        sort_col = getattr(Asset, sort_by, Asset.name)
        stmt = stmt.order_by(sort_col.desc() if sort_order == "desc" else sort_col.asc())
        stmt = stmt.offset(skip).limit(limit)

        res = await db.execute(stmt)
        return list(res.scalars().all()), total

    async def get_status_history(self, db: AsyncSession, asset_id: UUID) -> List[AssetStatusHistory]:
        stmt = (
            select(AssetStatusHistory)
            .where(AssetStatusHistory.asset_id == asset_id)
            .order_by(AssetStatusHistory.changed_at.desc())
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def add_status_history(
        self,
        db: AsyncSession,
        asset_id: UUID,
        previous_status: Optional[str],
        new_status: str,
        changed_by: Optional[UUID] = None,
        remarks: Optional[str] = None,
        reference_type: Optional[str] = None,
        reference_id: Optional[UUID] = None,
    ) -> None:
        entry = AssetStatusHistory(
            asset_id=asset_id,
            previous_status=previous_status,
            new_status=new_status,
            changed_by=changed_by,
            remarks=remarks,
            reference_type=reference_type,
            reference_id=reference_id,
            changed_at=datetime.now(timezone.utc),
        )
        db.add(entry)
        await db.flush()

    async def list_locations(self, db: AsyncSession) -> List[AssetLocation]:
        stmt = select(AssetLocation).where(AssetLocation.is_active == True).order_by(AssetLocation.name)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def list_bookable_assets(self, db: AsyncSession) -> List[Asset]:
        stmt = (
            select(Asset)
            .where(Asset.is_bookable == True, Asset.deleted_at.is_(None))
            .options(selectinload(Asset.category), selectinload(Asset.current_location))
            .order_by(Asset.name)
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())


asset_repo = AssetRepository()
