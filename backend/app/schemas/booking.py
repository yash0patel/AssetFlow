from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, model_validator


class BookingCreate(BaseModel):
    asset_id: UUID
    start_datetime: datetime
    end_datetime: datetime
    purpose: Optional[str] = Field(None, max_length=255)
    department_id: Optional[UUID] = None

    @model_validator(mode="after")
    def check_dates(self):
        if self.end_datetime <= self.start_datetime:
            raise ValueError("end_datetime must be after start_datetime")
        return self


class BookingResponse(BaseModel):
    id: UUID
    asset_id: UUID
    asset_name: Optional[str] = None
    asset_tag: Optional[str] = None
    booked_by_name: Optional[str] = None
    department_name: Optional[str] = None
    start_datetime: datetime
    end_datetime: datetime
    purpose: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class BookingListResponse(BaseModel):
    items: list[BookingResponse]
    total: int
    page: int
    page_size: int
    pages: int


class BookingCancelRequest(BaseModel):
    cancellation_reason: Optional[str] = None
