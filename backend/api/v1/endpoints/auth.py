from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ....core import security
from ....core.config import settings
from ....core.deps import get_current_user, get_current_active_user
from ....database import get_db
from ....models.user import User
from ....models.audit_log import AuditLog, AuditAction
from ....schemas.auth import UserCreate, UserResponse, Token

router = APIRouter()


@router.post("/register", response_model=Token)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Register new user.
    """
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    user = User(
        email=user_in.email,
        username=user_in.username,
        password_hash=security.get_password_hash(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create tokens
    access_token = security.create_access_token(
        data={"sub": user.id, "role": user.role}
    )
    refresh_token = security.create_refresh_token(
        data={"sub": user.id}
    )

    # Log registration
    audit_log = AuditLog(
        user_id=user.id,
        action=AuditAction.REGISTER,
    )
    db.add(audit_log)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/login", response_model=Token)
def login(
    request: Request,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = security.create_access_token(
        data={"sub": user.id, "role": user.role}
    )
    refresh_token = security.create_refresh_token(
        data={"sub": user.id}
    )

    # Log login
    audit_log = AuditLog(
        user_id=user.id,
        action=AuditAction.LOGIN,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(audit_log)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
def refresh_token(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Refresh access token.
    """
    access_token = security.create_access_token(
        data={"sub": current_user.id, "role": current_user.role}
    )
    refresh_token = security.create_refresh_token(
        data={"sub": current_user.id}
    )

    # Log token refresh
    audit_log = AuditLog(
        user_id=current_user.id,
        action=AuditAction.TOKEN_REFRESH,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(audit_log)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Logout user.
    """
    audit_log = AuditLog(
        user_id=current_user.id,
        action=AuditAction.LOGOUT,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(audit_log)
    db.commit()

    return {"message": "Successfully logged out"} 