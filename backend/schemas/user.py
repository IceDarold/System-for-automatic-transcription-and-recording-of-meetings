from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List
from datetime import datetime, date
from models.user import UserRole
from models.meeting import MeetingStatus, AccessLevel

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    middle_name: Optional[str] = None

class UserCreate(UserBase):
    password: constr(min_length=8)

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    password: Optional[constr(min_length=8)] = None

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MeetingResponse(BaseModel):
    id: int
    title: str
    status: MeetingStatus
    date: date
    access_level: AccessLevel

    class Config:
        from_attributes = True

class AuditLogResponse(BaseModel):
    action: str
    timestamp: datetime
    target: dict

    class Config:
        from_attributes = True 