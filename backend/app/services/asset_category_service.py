from typing import List, Optional, Tuple
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import AssetCategory
from app.repositories.asset_category_repository import asset_category_repo
from app.schemas.asset_category import AssetCategoryCreate, AssetCategoryUpdate
from app.utils.helpers import utcnow

class AssetCategoryService:
    async def create(
        self, db: AsyncSession, *, obj_in: AssetCategoryCreate
    ) -> AssetCategory:
        """Create an asset category and save its attributes."""
        # 1. Prevent duplicate name (case-insensitive)
        existing = await asset_category_repo.get_by_name(db, obj_in.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with name '{obj_in.name}' already exists."
            )

        # 2. Parent validation
        if obj_in.parent_category_id:
            parent = await asset_category_repo.get(db, obj_in.parent_category_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent category does not exist."
                )
            if not parent.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent category is inactive."
                )

        # Create
        cat = AssetCategory(
            name=obj_in.name,
            parent_category_id=obj_in.parent_category_id,
            description=obj_in.description,
            default_useful_life_months=obj_in.default_useful_life_months,
            is_active=obj_in.is_active
        )
        await asset_category_repo.create(db, obj_in=cat)

        # Attributes
        if obj_in.attributes:
            attrs = [attr.model_dump() for attr in obj_in.attributes]
            await asset_category_repo.save_attributes(db, cat.id, attrs)

        return cat

    async def update(
        self, db: AsyncSession, *, id: UUID, obj_in: AssetCategoryUpdate
    ) -> AssetCategory:
        """Update an asset category and its custom attributes."""
        cat = await asset_category_repo.get(db, id)
        if not cat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset category not found."
            )

        # Name check
        if obj_in.name and obj_in.name != cat.name:
            existing = await asset_category_repo.get_by_name(db, obj_in.name)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Category with name '{obj_in.name}' already exists."
                )
            cat.name = obj_in.name

        # Parent validation & loop check
        if obj_in.parent_category_id is not None and obj_in.parent_category_id != cat.parent_category_id:
            parent = await asset_category_repo.get(db, obj_in.parent_category_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent category does not exist."
                )
            if not parent.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent category is inactive."
                )
            
            # Loop check
            if await self._has_category_loop(db, id, obj_in.parent_category_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid hierarchy: A category cannot be a child of itself or one of its subcategories."
                )
            
            cat.parent_category_id = obj_in.parent_category_id

        # Update other fields
        if obj_in.description is not None:
            cat.description = obj_in.description
        if obj_in.default_useful_life_months is not None:
            cat.default_useful_life_months = obj_in.default_useful_life_months
        if obj_in.is_active is not None:
            cat.is_active = obj_in.is_active

        cat.updated_at = utcnow()

        # Update attributes if provided
        if obj_in.attributes is not None:
            attrs = [attr.model_dump() for attr in obj_in.attributes]
            await asset_category_repo.save_attributes(db, id, attrs)

        await db.flush()
        return cat

    async def delete(self, db: AsyncSession, *, id: UUID) -> AssetCategory:
        """Delete a category after verifying no assets are assigned to it."""
        cat = await asset_category_repo.get(db, id)
        if not cat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset category not found."
            )

        # Check assets presence
        has_assets = await asset_category_repo.check_assets_exist(db, id)
        if has_assets:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete category because active assets are assigned to it."
            )

        await asset_category_repo.delete(db, id=id)
        return cat

    async def _has_category_loop(self, db: AsyncSession, category_id: UUID, parent_id: UUID) -> bool:
        """Recursive/loop check to detect cyclical parent hierarchy for categories."""
        current_id = parent_id
        while current_id:
            if current_id == category_id:
                return True
            parent = await asset_category_repo.get(db, current_id)
            if not parent:
                break
            current_id = parent.parent_category_id
        return False

asset_category_service = AssetCategoryService()
