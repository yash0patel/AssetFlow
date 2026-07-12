from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

class EmployeeBase(BaseModel):
    department_id: Optional[UUID] = None
    designation: Optional[str] = Field(None, max_length=100)
    reporting_manager_id: Optional[UUID] = None
    date_of_joining: Optional[date] = None
    status: str = Field("Active", pattern="^(Active|Inactive)$")

class EmployeeCreate(EmployeeBase):
    user_id: UUID

class EmployeeUpdate(BaseModel):
    department_id: Optional[UUID] = None
    designation: Optional[str] = Field(None, max_length=100)
    reporting_manager_id: Optional[UUID] = None
    date_of_joining: Optional[date] = None
    status: Optional[str] = Field(None, pattern="^(Active|Inactive)$")

class EmployeeResponse(EmployeeBase):
    id: UUID
    user_id: UUID
    employee_code: str
    created_at: datetime
    updated_at: datetime
    
    # Extra fields populated from related tables
    name: str = ""
    email: str = ""
    department_name: Optional[str] = None
    reporting_manager_name: Optional[str] = None
    role: str = "Employee"

    class Config:
        from_attributes = True

class EmployeeListResponse(BaseModel):
    items: list[EmployeeResponse]
    total: int
    page: int
    page_size: int
    pages: int

class RolePromotionRequest(BaseModel):
    role: str = Field(..., pattern="^(Admin|Asset Manager|Department Head|Employee)$")
    department_scope_id: Optional[UUID] = None

class UserWithoutEmployeeResponse(BaseModel):
    id: UUID
    email: str
    name: str

    class Config:
        from_attributes = True
