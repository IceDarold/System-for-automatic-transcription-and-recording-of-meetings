from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum, ForeignKey, Table, Text, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
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
    date = Column(DateTime(timezone=True), nullable=False)
    short_description = Column(Text, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    access_level = Column(Enum(AccessLevel), default=AccessLevel.private, nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # New fields for processing status
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

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    meetings = relationship("Meeting", secondary=meeting_tags, back_populates="tags") 