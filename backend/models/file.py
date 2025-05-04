from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from database import Base

class FileType(str, enum.Enum):
    audio = "audio"
    transcript = "transcript"
    summary = "summary"
    protocol = "protocol"
    thumbnail = "thumbnail"

    def __str__(self) -> str:
        return self.value

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_type = Column(Enum(FileType), nullable=False)
    mime_type = Column(String, nullable=False)
    size = Column(Integer, nullable=False)  # size in bytes
    url = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    meeting = relationship("Meeting", back_populates="files") 