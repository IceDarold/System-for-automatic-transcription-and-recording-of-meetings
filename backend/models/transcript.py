from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from database import Base

class TranscriptBlock(Base):
    __tablename__ = "transcript_blocks"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)
    speaker_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for unknown speakers
    start_time = Column(Float, nullable=False)  # Start time in seconds
    end_time = Column(Float, nullable=False)    # End time in seconds
    text = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)  # Confidence score 0-1
    language = Column(String(2), nullable=False, default="ru")  # ISO 639-1 language code
    metadata = Column(JSON, nullable=True)      # Additional metadata as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    meeting = relationship("Meeting", back_populates="transcript_blocks")
    speaker = relationship("User", back_populates="transcript_blocks") 