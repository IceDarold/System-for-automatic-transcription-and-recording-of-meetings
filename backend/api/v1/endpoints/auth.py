from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from core import security
from core.config import settings
from core.auth import get_current_user
from database import get_db
from models.user import User, UserRole
from models.audit_log import AuditLog, AuditAction
from schemas.auth import UserCreate, UserResponse, Token

router = APIRouter()


@router.post("/register", response_model=Token)
def register(
    request: Request,
    db: Session = Depends(get_db),
    first_name: str = Form(...),
    last_name: str = Form(...),
    middle_name: str = Form(None),
    email: str = Form(...),
    password: str = Form(...),
) -> Any:
    """
    Register new user (form-data).
    - **email**: Email пользователя (уникальный)
    - **first_name**: Имя пользователя
    - **last_name**: Фамилия пользователя
    - **middle_name**: Отчество пользователя (опционально)
    - **password**: Пароль пользователя
    """
    import re
    if not re.fullmatch(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$".strip(), email):
        raise HTTPException(
            status_code=400,
            detail="Invalid email format. Please enter a valid email address."
        )
    
    # Проверка на пустые поля
    if not first_name or not first_name.strip():
        raise HTTPException(
            status_code=400,
            detail="First name cannot be empty."
        )
    
    if not last_name or not last_name.strip():
        raise HTTPException(
            status_code=400,
            detail="Last name cannot be empty."
        )
    
    if not password or len(password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 6 characters long."
        )
    
    # Проверка на существующего пользователя
    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    try:
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            password_hash=security.get_password_hash(password),
            role="user"
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
            action=AuditAction.register,
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
    except ValueError as e:
        # Отлов ошибок валидации модели
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        # Отлов прочих ошибок
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(e)}",
        )


@router.post("/login", response_model=Token)
def login(
    request: Request,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    try:
        import re
        if not re.fullmatch(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$".strip(), form_data.username):
            raise HTTPException(
                status_code=400,
                detail="Invalid email format. Please enter a valid email address."
            )
            
        user = db.query(User).filter(User.email == form_data.username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User with this email not found.",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        if not security.verify_password(form_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password.",
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
            action=AuditAction.login,
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
    except HTTPException:
        # Пробрасываем HTTP ошибки дальше
        raise
    except Exception as e:
        # Отлов прочих ошибок
        raise HTTPException(
            status_code=500,
            detail=f"Login failed: {str(e)}",
        )


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
        action=AuditAction.token_refresh,
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
        action=AuditAction.logout,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(audit_log)
    db.commit()

    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get current user information.
    """
    return current_user 