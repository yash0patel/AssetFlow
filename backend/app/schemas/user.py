"""
app/schemas/user.py
───────────────────
Pydantic schemas for user profile operations.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    status: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    status: Optional[str] = None


class UserProfileBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    phone_number: Optional[str] = None


class UserProfileResponse(UserProfileBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserDetailResponse(UserBase):
    id: UUID
    created_at: datetime
    profile: Optional[UserProfileResponse] = None

    class Config:
        from_attributes = True
