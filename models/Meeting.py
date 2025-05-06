from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date, time

class Meeting(BaseModel):
    id: int
    title: str
    date: date
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    duration: Optional[int] = None
    location: Optional[str] = None
    is_online: bool = False
    is_published: bool = False
    access_level: str
    created_by_id: int
    created_at: str
    updated_at: Optional[str] = None
    status: str
    processing_progress: int = 0
    error_message: Optional[str] = None
    
    # File IDs
    audio_file_id: Optional[int] = None
    transcript_file_id: Optional[int] = None
    summary_file_id: Optional[int] = None
    protocol_file_id: Optional[int] = None
    
    # Relationships
    participants: List[Dict[str, Any]] = []
    tags: List[Dict[str, Any]] = []
    
    # Content fields
    transcript: Optional[str] = None
    summary: Optional[str] = None
    decisions: List[str] = []
    
    class Config:
        from_attributes = True 