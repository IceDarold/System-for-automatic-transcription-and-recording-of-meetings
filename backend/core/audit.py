from sqlalchemy.orm import Session
from models.audit_log import AuditLog, AuditAction
from datetime import datetime

async def log_action(
    db: Session,
    user_id: int,
    action: str,
    resource_id: int = None,
    resource_type: str = None,
    metadata: dict = None
) -> None:
    """
    Log a user action in the audit log.
    
    Args:
        db: Database session
        user_id: ID of the user performing the action
        action: Type of action (e.g., 'view_meeting', 'create_meeting')
        resource_id: ID of the resource being acted upon (optional)
        resource_type: Type of resource (e.g., 'meeting', 'user') (optional)
        metadata: Additional metadata about the action (optional)
    """
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_id=resource_id,
        resource_type=resource_type,
        metadata=metadata,
        created_at=datetime.utcnow()
    )
    
    db.add(audit_log)
    db.commit() 