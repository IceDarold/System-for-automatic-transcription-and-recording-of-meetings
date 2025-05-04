from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TagResponse(BaseModel):
    id: int
    label: str

class UserResponse(BaseModel):
    id: int
    name: str

class MeetingResponse(BaseModel):
    id: int
    title: str
    date: str  # ISO8601 format
    tags: List[TagResponse]
    participants: List[UserResponse]
    created_by: UserResponse
    short_description: Optional[str]
    thumbnail_url: Optional[str]

class MeetingListResponse(BaseModel):
    items: List[MeetingResponse]
    has_more: bool 