from sqlalchemy.orm import Session
from models.audit_log import AuditLog, AuditAction
from datetime import datetime

async def log_action(
    db: Session,
    user_id: int,
    action: str,
    resource_id: int = None,
    resource_type: str = None,
    audit_metadata: dict = None,
    ip_address: str = None,
    user_agent: str = None
) -> None:
    """
    Log an action in the audit log.
    
    Args:
        db: Database session
        user_id: ID of the user performing the action
        action: Type of action (must be one of AuditAction values)
        resource_id: ID of the resource being acted upon (optional)
        resource_type: Type of the resource (optional)
        audit_metadata: Additional metadata about the action (optional)
        ip_address: IP address of the user (optional)
        user_agent: User agent string (optional)
    """
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_id=resource_id,
        resource_type=resource_type,
        audit_metadata=audit_metadata,
        ip_address=ip_address,
        user_agent=user_agent,
        created_at=datetime.utcnow()
    )
    
    db.add(audit_log)
    db.commit() 