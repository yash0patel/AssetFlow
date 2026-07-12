from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class MaintenanceCreate(BaseModel):
    asset_id: UUID
    issue_description: str = Field(..., min_length=1)
    priority: str = Field("Medium", pattern="^(Low|Medium|High|Critical)$")


class MaintenanceApprove(BaseModel):
    technician_id: Optional[UUID] = None


class MaintenanceAssign(BaseModel):
    technician_id: UUID


class MaintenanceReject(BaseModel):
    rejection_reason: str = Field(..., min_length=1)


class MaintenanceResolve(BaseModel):
    resolution_notes: Optional[str] = None
    actual_cost: Optional[float] = None


class TechnicianResponse(BaseModel):
    id: UUID
    name: str
    specialization: Optional[str] = None
    is_external_vendor: bool
    vendor_name: Optional[str] = None
    contact_number: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class MaintenanceResponse(BaseModel):
    id: UUID
    request_code: str
    asset_id: UUID
    asset_tag: Optional[str] = None
    asset_name: Optional[str] = None
    raised_by_name: Optional[str] = None
    issue_description: str
    priority: str
    status: str
    technician_id: Optional[UUID] = None
    technician_name: Optional[str] = None
    rejection_reason: Optional[str] = None
    resolution_notes: Optional[str] = None
    approved_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MaintenanceListResponse(BaseModel):
    items: list[MaintenanceResponse]
    total: int
    page: int
    page_size: int
    pages: int
