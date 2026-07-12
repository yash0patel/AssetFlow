from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy import select, or_, text, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.department import AssetCategory, AssetCategoryAttribute
from app.models.asset import Asset
from app.repositories.base_repository import BaseRepository

class AssetCategoryRepository(BaseRepository[AssetCategory]):
    def __init__(self):
        super().__init__(AssetCategory)

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[AssetCategory]:
        """Fetch asset category by name (case-insensitive)."""
        stmt = select(AssetCategory).where(text("lower(name) = :name")).params(name=name.lower())
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_categories(
        self,
        db: AsyncSession,
        *,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        parent_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "name",
        sort_order: str = "asc"
    ) -> Tuple[List[AssetCategory], int]:
        """List asset categories with filtering, search, and sorting."""
        stmt = select(AssetCategory)

        # Filters
        if search:
            stmt = stmt.where(
                or_(
                    AssetCategory.name.ilike(f"%{search}%"),
                    AssetCategory.description.ilike(f"%{search}%")
                )
            )
        if is_active is not None:
            stmt = stmt.where(AssetCategory.is_active == is_active)
        if parent_id is not None:
            stmt = stmt.where(AssetCategory.parent_category_id == parent_id)

        # Count total
        count_stmt = select(text("count(*)")).select_from(stmt.subquery())
        total_res = await db.execute(count_stmt)
        total = total_res.scalar_one()

        # Eager load attributes and parent details
        stmt = stmt.options(
            selectinload(AssetCategory.parent_category),
            selectinload(AssetCategory.attributes)
        )

        # Sorting
        sort_attr = getattr(AssetCategory, sort_by, AssetCategory.name)
        if sort_order.lower() == "desc":
            stmt = stmt.order_by(sort_attr.desc())
        else:
            stmt = stmt.order_by(sort_attr.asc())

        # Pagination
        stmt = stmt.offset(skip).limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars().all()), total

    async def check_assets_exist(self, db: AsyncSession, category_id: UUID) -> bool:
        """Check if any assets are linked to this category."""
        stmt = select(Asset).where(Asset.category_id == category_id).limit(1)
        res = await db.execute(stmt)
        return res.scalar_one_or_none() is not None

    async def save_attributes(
        self, db: AsyncSession, category_id: UUID, attributes_list: List[dict]
    ) -> None:
        """Save (replace) all attributes for a given category."""
        # 1. Delete existing attributes
        stmt_del = delete(AssetCategoryAttribute).where(AssetCategoryAttribute.category_id == category_id)
        await db.execute(stmt_del)

        # 2. Insert new attributes
        for idx, attr_data in enumerate(attributes_list):
            attr = AssetCategoryAttribute(
                category_id=category_id,
                attribute_key=attr_data["attribute_key"],
                attribute_label=attr_data["attribute_label"],
                data_type=attr_data["data_type"],
                select_options=attr_data.get("select_options"),
                is_required=attr_data.get("is_required", False),
                display_order=attr_data.get("display_order", idx)
            )
            db.add(attr)
        await db.flush()

asset_category_repo = AssetCategoryRepository()
