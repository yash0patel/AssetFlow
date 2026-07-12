from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AssetLocationResponse(BaseModel):
    id: UUID
    name: str
    location_type: str

    class Config:
        from_attributes = True


class AssetStatusHistoryResponse(BaseModel):
    id: int
    previous_status: Optional[str] = None
    new_status: str
    reference_type: Optional[str] = None
    remarks: Optional[str] = None
    changed_at: datetime

    class Config:
        from_attributes = True


class AssetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    category_id: UUID
    serial_number: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    acquisition_date: Optional[date] = None
    acquisition_cost: Optional[Decimal] = Field(None, ge=0)
    condition: str = Field("Good", pattern="^(New|Good|Fair|Poor|Damaged)$")
    location_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    is_bookable: bool = False
    warranty_expiry_date: Optional[date] = None
    expected_retirement_date: Optional[date] = None


class AssetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    serial_number: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    condition: Optional[str] = Field(None, pattern="^(New|Good|Fair|Poor|Damaged)$")
    current_status: Optional[str] = Field(
        None,
        pattern="^(Available|Allocated|Reserved|Under Maintenance|Lost|Retired|Disposed)$",
    )
    location_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    is_bookable: Optional[bool] = None
    warranty_expiry_date: Optional[date] = None
    expected_retirement_date: Optional[date] = None
    status_remarks: Optional[str] = None


class AssetResponse(BaseModel):
    id: UUID
    asset_tag: str
    name: str
    category_id: UUID
    category_name: Optional[str] = None
    serial_number: Optional[str] = None
    description: Optional[str] = None
    acquisition_date: Optional[date] = None
    acquisition_cost: Optional[Decimal] = None
    condition: str
    current_status: str
    location_id: Optional[UUID] = None
    location_name: Optional[str] = None
    department_id: Optional[UUID] = None
    department_name: Optional[str] = None
    is_bookable: bool
    warranty_expiry_date: Optional[date] = None
    expected_retirement_date: Optional[date] = None
    current_holder_employee_id: Optional[UUID] = None
    current_holder_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssetDetailResponse(AssetResponse):
    status_history: List[AssetStatusHistoryResponse] = []


class AssetListResponse(BaseModel):
    items: List[AssetResponse]
    total: int
    page: int
    page_size: int
    pages: int
