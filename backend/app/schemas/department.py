from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

class DepartmentBase(BaseModel):
    name: str = Field(..., max_length=150)
    code: Optional[str] = Field(None, max_length=20)
    parent_department_id: Optional[UUID] = None
    primary_location_id: Optional[UUID] = None
    status: str = Field("Active", pattern="^(Active|Inactive)$")

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=150)
    code: Optional[str] = Field(None, max_length=20)
    parent_department_id: Optional[UUID] = None
    primary_location_id: Optional[UUID] = None
    status: Optional[str] = Field(None, pattern="^(Active|Inactive)$")
    head_employee_id: Optional[UUID] = None

class DepartmentResponse(DepartmentBase):
    id: UUID
    head_employee_id: Optional[UUID] = None
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    
    # Extra fields for frontend presentation
    parent_name: Optional[str] = None
    head_name: Optional[str] = None

    class Config:
        from_attributes = True

class DepartmentListResponse(BaseModel):
    items: list[DepartmentResponse]
    total: int
    page: int
    page_size: int
    pages: int
