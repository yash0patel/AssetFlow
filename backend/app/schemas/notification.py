from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: int
    notification_type: str
    category: str
    title: str
    message: str
    reference_type: Optional[str] = None
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    total: int
    page: int
    page_size: int
    pages: int
    unread_count: int
