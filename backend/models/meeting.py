from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum, ForeignKey, Table, Text, Float, Date, Time
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from database import Base

# Association tables for many-to-many relationships
meeting_tags = Table(
    'meeting_tags',
    Base.metadata,
    Column('meeting_id', Integer, ForeignKey('meetings.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

meeting_participants = Table(
    'meeting_participants',
    Base.metadata,
    Column('meeting_id', Integer, ForeignKey('meetings.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)

meeting_access = Table(
    'meeting_access',
    Base.metadata,
    Column('meeting_id', Integer, ForeignKey('meetings.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)

class AccessLevel(str, enum.Enum):
    public = "public"
    restricted = "restricted"
    private = "private"

    def __str__(self) -> str:
        return self.value

class MeetingStatus(str, enum.Enum):
    pending = "pending"      # Ожидает обработки
    processing = "processing" # В процессе
    done = "done"           # Обработка завершена
    failed = "failed"       # Ошибка обработки

    def __str__(self) -> str:
        return self.value

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    duration = Column(Integer, nullable=True)  # в секундах
    location = Column(String, nullable=True)
    is_online = Column(Boolean, default=False, nullable=False)
    is_published = Column(Boolean, default=False, nullable=False)
    access_level = Column(Enum(AccessLevel), default=AccessLevel.private, nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Fields for processing status
    status = Column(Enum(MeetingStatus), default=MeetingStatus.pending, nullable=False)
    processing_progress = Column(Integer, default=0)  # 0-100%
    error_message = Column(Text, nullable=True)

    # File relationships
    audio_file_id = Column(Integer, ForeignKey("files.id"), nullable=True)
    transcript_file_id = Column(Integer, ForeignKey("files.id"), nullable=True)
    summary_file_id = Column(Integer, ForeignKey("files.id"), nullable=True)
    protocol_file_id = Column(Integer, ForeignKey("files.id"), nullable=True)

    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_id])
    tags = relationship("Tag", secondary=meeting_tags, back_populates="meetings")
    participants = relationship("User", secondary=meeting_participants, back_populates="participated_meetings")
    access_users = relationship("User", secondary=meeting_access, back_populates="accessible_meetings")
    
    # New relationships
    files = relationship("File", primaryjoin="and_(File.meeting_id==Meeting.id, File.meeting_id!=None)", back_populates="meeting")
    transcript_blocks = relationship("TranscriptBlock", back_populates="meeting")
    
    # File relationships
    audio_file = relationship("File", foreign_keys=[audio_file_id])
    transcript_file = relationship("File", foreign_keys=[transcript_file_id])
    summary_file = relationship("File", foreign_keys=[summary_file_id])
    protocol_file = relationship("File", foreign_keys=[protocol_file_id])

    @property
    def is_ready(self) -> bool:
        return self.status == MeetingStatus.done

    def __init__(self, **kwargs):
        # Validate title
        if not kwargs.get("title"):
            raise ValueError("Title is required")
        
        # Validate date
        date = kwargs.get("date")
        if not date:
            raise ValueError("Date is required")
        if isinstance(date, str):
            try:
                kwargs["date"] = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Invalid date format. Use YYYY-MM-DD")
        
        # Validate time fields
        start_time = kwargs.get("start_time")
        end_time = kwargs.get("end_time")
        if start_time and isinstance(start_time, str):
            try:
                kwargs["start_time"] = datetime.strptime(start_time, "%H:%M:%S").time()
            except ValueError:
                raise ValueError("Invalid start time format. Use HH:MM:SS")
        if end_time and isinstance(end_time, str):
            try:
                kwargs["end_time"] = datetime.strptime(end_time, "%H:%M:%S").time()
            except ValueError:
                raise ValueError("Invalid end time format. Use HH:MM:SS")
        
        # Validate duration
        duration = kwargs.get("duration")
        if duration is not None and duration < 0:
            raise ValueError("Duration cannot be negative")
        
        # Validate access level
        access_level = kwargs.get("access_level")
        if access_level and access_level not in [level.value for level in AccessLevel]:
            raise ValueError(f"Invalid access level. Must be one of: {[level.value for level in AccessLevel]}")
        
        # Validate status
        status = kwargs.get("status")
        if status and status not in [status.value for status in MeetingStatus]:
            raise ValueError(f"Invalid status. Must be one of: {[status.value for status in MeetingStatus]}")
        
        # TODO: Add validation to ensure end_time is not before start_time if both are provided.

        super().__init__(**kwargs)

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    meetings = relationship("Meeting", secondary=meeting_tags, back_populates="tags")

    def __init__(self, **kwargs):
        # Validate label
        if not kwargs.get("label"):
            raise ValueError("Label is required")
        if len(kwargs["label"].strip()) == 0:
            raise ValueError("Label cannot be empty")
        
        super().__init__(**kwargs) 