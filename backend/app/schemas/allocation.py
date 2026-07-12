from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class AllocationCreate(BaseModel):
    asset_id: UUID
    allocated_to_employee_id: Optional[UUID] = None
    allocated_to_department_id: Optional[UUID] = None
    expected_return_date: Optional[date] = None

    class Config:
        from_attributes = True


class ReturnRequest(BaseModel):
    return_condition: str = Field("Good", pattern="^(New|Good|Fair|Poor|Damaged)$")
    return_notes: Optional[str] = None


class AllocationResponse(BaseModel):
    id: UUID
    asset_id: UUID
    asset_tag: Optional[str] = None
    asset_name: Optional[str] = None
    allocated_to_employee_id: Optional[UUID] = None
    allocated_to_employee_name: Optional[str] = None
    allocated_to_department_id: Optional[UUID] = None
    allocated_to_department_name: Optional[str] = None
    allocated_by_name: Optional[str] = None
    allocation_date: datetime
    expected_return_date: Optional[date] = None
    actual_return_date: Optional[datetime] = None
    return_condition: Optional[str] = None
    return_notes: Optional[str] = None
    status: str
    is_overdue: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class AllocationListResponse(BaseModel):
    items: list[AllocationResponse]
    total: int
    page: int
    page_size: int
    pages: int


class TransferRequestCreate(BaseModel):
    to_employee_id: Optional[UUID] = None
    to_department_id: Optional[UUID] = None
    reason: Optional[str] = None


class TransferResponse(BaseModel):
    id: UUID
    asset_id: UUID
    asset_tag: Optional[str] = None
    asset_name: Optional[str] = None
    from_employee_name: Optional[str] = None
    to_employee_name: Optional[str] = None
    to_department_name: Optional[str] = None
    requested_by_name: Optional[str] = None
    reason: Optional[str] = None
    status: str
    approved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TransferListResponse(BaseModel):
    items: list[TransferResponse]
    total: int
    page: int
    page_size: int
    pages: int


class TransferActionRequest(BaseModel):
    rejection_reason: Optional[str] = None
