from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
import re
from database import Base


class UserRole(str, enum.Enum):
    user = "user"
    editor = "editor"
    superadmin = "superadmin"

    def __str__(self) -> str:
        return self.value

    def __str__(self):
        return self.value


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    created_meetings = relationship("Meeting", back_populates="created_by", foreign_keys="Meeting.created_by_id")
    participated_meetings = relationship("Meeting", secondary="meeting_participants", back_populates="participants")
    accessible_meetings = relationship("Meeting", secondary="meeting_access", back_populates="access_users")
    transcript_blocks = relationship("TranscriptBlock", back_populates="speaker")

    def __init__(self, **kwargs):
        # Validate email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", kwargs.get("email", "")):
            raise ValueError("Invalid email format")
        
        # Validate required fields
        if not kwargs.get("first_name"):
            raise ValueError("First name is required")
        if not kwargs.get("last_name"):
            raise ValueError("Last name is required")
        if not kwargs.get("password_hash"):
            raise ValueError("Password hash is required")
        
        super().__init__(**kwargs)
