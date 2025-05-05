from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from models.meeting import MeetingStatus, AccessLevel
from models.file import FileType

class TagResponse(BaseModel):
    id: int
    label: str

class UserResponse(BaseModel):
    id: int
    name: str
    role: Optional[str] = None

class FileResponse(BaseModel):
    id: int
    filename: str
    file_type: FileType
    mime_type: str
    size: int
    url: str
    created_at: datetime

class TranscriptBlockResponse(BaseModel):
    speaker: Optional[UserResponse]
    start: float
    end: float
    text: str
    confidence: float
    language: str
    metadata: Optional[Dict[str, Any]] = None

class MeetingResponse(BaseModel):
    id: int
    title: str
    date: datetime
    tags: List[TagResponse]
    participants: List[UserResponse]
    created_by: UserResponse
    short_description: Optional[str]
    thumbnail_url: Optional[str]
    access_level: AccessLevel
    status: MeetingStatus
    processing_progress: int = Field(ge=0, le=100)
    is_ready: bool
    created_at: datetime
    updated_at: datetime

class MeetingDetailResponse(MeetingResponse):
    audio_url: Optional[str]
    transcript: Optional[List[TranscriptBlockResponse]]
    summary: Optional[str]
    protocol: Optional[str]
    error_message: Optional[str]

class MeetingSearchParams(BaseModel):
    search: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    participant_ids: Optional[List[int]] = None
    tag_ids: Optional[List[int]] = None
    team_ids: Optional[List[int]] = None
    access_level: Optional[AccessLevel] = None
    status: Optional[MeetingStatus] = None
    created_by_id: Optional[int] = None
    sort: str = Field("created_at_desc", pattern="^(created_at_desc|created_at_asc|date_desc|date_asc)$")
    limit: int = Field(10, ge=1, le=50)
    offset: int = Field(0, ge=0)

class MeetingListResponse(BaseModel):
    items: List[MeetingResponse]
    has_more: bool
    total: int
    filters: Optional[Dict[str, Any]] = None 