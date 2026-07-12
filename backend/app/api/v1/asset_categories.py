from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.department import AssetCategory
from app.repositories.user_repository import user_repo
from app.repositories.asset_category_repository import asset_category_repo
from app.schemas.asset_category import (
    AssetCategoryCreate,
    AssetCategoryListResponse,
    AssetCategoryResponse,
    AssetCategoryUpdate,
)
from app.services.asset_category_service import asset_category_service

router = APIRouter()

async def require_admin_or_manager(db: AsyncSession, user: User) -> None:
    role_name = await user_repo.get_user_role_name(db, user.id)
    if role_name not in ("admin", "super_admin", "manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Manager or Administrator privileges required."
        )

def build_category_response(cat: AssetCategory) -> dict:
    """Helper to convert AssetCategory model to dict schema."""
    parent_name = cat.parent_category.name if cat.parent_category else None
    
    attributes = []
    if cat.attributes:
        for attr in cat.attributes:
            attributes.append({
                "id": attr.id,
                "category_id": attr.category_id,
                "attribute_key": attr.attribute_key,
                "attribute_label": attr.attribute_label,
                "data_type": attr.data_type,
                "select_options": attr.select_options,
                "is_required": attr.is_required,
                "display_order": attr.display_order
            })
            
    return {
        "id": cat.id,
        "name": cat.name,
        "parent_category_id": cat.parent_category_id,
        "description": cat.description,
        "default_useful_life_months": cat.default_useful_life_months,
        "is_active": cat.is_active,
        "created_at": cat.created_at,
        "updated_at": cat.updated_at,
        "attributes": attributes,
        "parent_name": parent_name
    }

@router.get("/", response_model=AssetCategoryListResponse)
async def list_categories(
    search: Optional[str] = Query(None, description="Search term for name or description"),
    is_active: Optional[bool] = Query(None, description="Filter active categories"),
    parent_id: Optional[UUID] = Query(None, description="Filter by parent category ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    sort_by: str = Query("name"),
    sort_order: str = Query("asc"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List asset categories with filtering and sorting."""
    await require_admin_or_manager(db, current_user)
    
    skip = (page - 1) * page_size
    cats, total = await asset_category_repo.list_categories(
        db,
        search=search,
        is_active=is_active,
        parent_id=parent_id,
        skip=skip,
        limit=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    items = [build_category_response(c) for c in cats]
    pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    return AssetCategoryListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )

@router.post("/", response_model=AssetCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: AssetCategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new asset category."""
    await require_admin_or_manager(db, current_user)
    
    async with db.begin_nested():
        cat = await asset_category_service.create(db, obj_in=payload)
    await db.commit()
    
    # Reload category with attributes
    stmt = select(AssetCategory).where(AssetCategory.id == cat.id).options(
        selectinload(AssetCategory.parent_category),
        selectinload(AssetCategory.attributes)
    )
    res = await db.execute(stmt)
    db_cat = res.scalar_one()
    return build_category_response(db_cat)

@router.get("/{id}", response_model=AssetCategoryResponse)
async def get_category(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch details of a single category."""
    await require_admin_or_manager(db, current_user)
    
    stmt = select(AssetCategory).where(AssetCategory.id == id).options(
        selectinload(AssetCategory.parent_category),
        selectinload(AssetCategory.attributes)
    )
    res = await db.execute(stmt)
    cat = res.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")
        
    return build_category_response(cat)

@router.put("/{id}", response_model=AssetCategoryResponse)
async def update_category(
    id: UUID,
    payload: AssetCategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update details of a category."""
    await require_admin_or_manager(db, current_user)
    
    async with db.begin_nested():
        cat = await asset_category_service.update(db, id=id, obj_in=payload)
    await db.commit()
    
    stmt = select(AssetCategory).where(AssetCategory.id == id).options(
        selectinload(AssetCategory.parent_category),
        selectinload(AssetCategory.attributes)
    )
    res = await db.execute(stmt)
    db_cat = res.scalar_one()
    return build_category_response(db_cat)

@router.delete("/{id}", response_model=AssetCategoryResponse)
async def delete_category(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a category."""
    await require_admin_or_manager(db, current_user)
    
    async with db.begin_nested():
        cat = await asset_category_service.delete(db, id=id)
    await db.commit()
    
    return build_category_response(cat)
