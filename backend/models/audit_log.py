from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.sql import func
import enum
from database import Base


class AuditAction(str, enum.Enum):
    login = "login"
    logout = "logout"
    register = "register"
    token_refresh = "token_refresh"
    view_meeting = "view_meeting"
    create_meeting = "create_meeting"
    update_meeting = "update_meeting"
    delete_meeting = "delete_meeting"

    def __str__(self) -> str:
        return self.value


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    resource_id = Column(Integer, nullable=True)
    resource_type = Column(String, nullable=True)
    audit_metadata = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 