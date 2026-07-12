from datetime import date, datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class AuditCycleCreate(BaseModel):
    cycle_name: str = Field(..., min_length=1, max_length=150)
    start_date: date
    end_date: date
    scope_department_id: Optional[UUID] = None
    scope_location_id: Optional[UUID] = None
    auditor_ids: List[UUID] = []


class AuditItemVerify(BaseModel):
    verification_status: str = Field(..., pattern="^(Verified|Missing|Damaged)$")
    remarks: Optional[str] = None


class AuditCycleResponse(BaseModel):
    id: UUID
    cycle_name: str
    start_date: date
    end_date: date
    status: str
    scope_department_name: Optional[str] = None
    scope_location_name: Optional[str] = None
    creator_name: Optional[str] = None
    auditor_count: int = 0
    item_count: int = 0
    verified_count: int = 0
    discrepancy_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class AuditItemResponse(BaseModel):
    id: int
    audit_cycle_id: UUID
    asset_id: UUID
    asset_tag: Optional[str] = None
    asset_name: Optional[str] = None
    verification_status: str
    verified_by_name: Optional[str] = None
    verified_at: Optional[datetime] = None
    remarks: Optional[str] = None

    class Config:
        from_attributes = True


class AuditListResponse(BaseModel):
    items: List[AuditCycleResponse]
    total: int
    page: int
    page_size: int
    pages: int
