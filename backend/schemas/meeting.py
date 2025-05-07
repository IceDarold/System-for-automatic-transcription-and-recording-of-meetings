from pydantic import BaseModel, Field, ConfigDict, field_serializer
from typing import List, Optional, Dict, Any
from datetime import datetime, time
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

    model_config = ConfigDict(from_attributes=True)

class TranscriptBlockResponse(BaseModel):
    speaker: Optional[UserResponse]
    start: float
    end: float
    text: str
    confidence: float
    language: str
    metadata: Optional[Dict[str, Any]] = None

class MeetingBase(BaseModel):
    title: str
    date: datetime
    description: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    duration: Optional[int] = None
    location: Optional[str] = None
    is_online: bool = False
    is_published: bool = False
    access_level: AccessLevel = AccessLevel.private

class MeetingCreate(MeetingBase):
    pass

class MeetingUpdate(MeetingBase):
    pass

class MeetingResponse(MeetingBase):
    id: int
    created_by_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: MeetingStatus
    processing_progress: int = 0
    error_message: Optional[str] = None
    audio_url: Optional[str] = None
    transcript: Optional[List[Dict[str, Any]]] = []
    summary: Optional[str] = None
    protocol: Optional[str] = None
    tags: List[TagResponse] = []
    participants: List[Dict[str, Any]] = []

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('created_at')
    def serialize_created_at(self, v: datetime) -> str:
        return v.isoformat()

    @field_serializer('updated_at', when_used='json-unless-none')
    def serialize_updated_at(self, v: Optional[datetime]) -> Optional[str]:
        if v is None:
            return None
        return v.isoformat()

    @field_serializer('start_time', 'end_time', when_used='json-unless-none')
    def serialize_optional_time(self, v: Optional[time]) -> Optional[str]:
        if v is None:
            return None
        return v.strftime("%H:%M:%S")

class MeetingDetailResponse(MeetingResponse):
    transcript_blocks: List[Dict[str, Any]] = []
    files: List[FileResponse] = []

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

class MeetingCreate(BaseModel):
    title: str
    date: datetime
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    duration: Optional[int] = None  # in seconds
    location: Optional[str] = None
    is_online: bool = False
    description: Optional[str] = None
    access_level: AccessLevel = AccessLevel.private 