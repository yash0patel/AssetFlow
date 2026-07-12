from datetime import datetime
from typing import Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field

class AssetCategoryAttributeBase(BaseModel):
    attribute_key: str = Field(..., max_length=50)
    attribute_label: str = Field(..., max_length=100)
    data_type: str = Field(..., pattern="^(TEXT|NUMBER|DATE|BOOLEAN|SELECT)$")
    select_options: Optional[Any] = None
    is_required: bool = False
    display_order: int = 0

class AssetCategoryAttributeResponse(AssetCategoryAttributeBase):
    id: UUID
    category_id: UUID

    class Config:
        from_attributes = True

class AssetCategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    parent_category_id: Optional[UUID] = None
    description: Optional[str] = None
    default_useful_life_months: Optional[int] = None
    is_active: bool = True

class AssetCategoryCreate(AssetCategoryBase):
    attributes: Optional[list[AssetCategoryAttributeBase]] = None

class AssetCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    parent_category_id: Optional[UUID] = None
    description: Optional[str] = None
    default_useful_life_months: Optional[int] = None
    is_active: Optional[bool] = None
    attributes: Optional[list[AssetCategoryAttributeBase]] = None

class AssetCategoryResponse(AssetCategoryBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    attributes: list[AssetCategoryAttributeResponse] = []
    parent_name: Optional[str] = None

    class Config:
        from_attributes = True

class AssetCategoryListResponse(BaseModel):
    items: list[AssetCategoryResponse]
    total: int
    page: int
    page_size: int
    pages: int
