from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.user import User, UserRole
from core.security import get_current_user as aliased_security_get_current_user, oauth2_scheme

# get_current_user from this module is now the one from core.security
get_current_user = aliased_security_get_current_user

# oauth2_scheme is imported for clarity as it's a dependency for aliased_security_get_current_user.

# get_current_active_user was removed as its functionality (checking is_active)
# is already part of aliased_security_get_current_user.

def require_superadmin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user 