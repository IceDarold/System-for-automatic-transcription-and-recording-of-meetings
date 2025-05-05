from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models.user import User
from schemas.user import UserResponse, UserUpdate, MeetingResponse, AuditLogResponse
from core.security import get_current_user, get_password_hash

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get information about the current user
    """
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update information about the current user
    """
    # Update user fields if provided
    if user_update.first_name is not None:
        current_user.first_name = user_update.first_name
    if user_update.last_name is not None:
        current_user.last_name = user_update.last_name
    if user_update.middle_name is not None:
        current_user.middle_name = user_update.middle_name
    if user_update.password is not None:
        current_user.password_hash = get_password_hash(user_update.password)

    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/me/meetings", response_model=List[MeetingResponse])
async def get_user_meetings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of meetings created by the current user
    """
    return current_user.created_meetings

@router.get("/me/logs", response_model=List[AuditLogResponse])
async def get_user_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get audit logs for the current user
    """
    # Check if audit_log table exists
    try:
        from models.audit_log import AuditLog
        logs = db.query(AuditLog).filter(
            AuditLog.user_id == current_user.id
        ).order_by(AuditLog.timestamp.desc()).all()
        return logs
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Audit logging is not implemented"
        ) 