"""
FastAPI dependencies — DB session, current user, role verification, and geographic scope enforcement.
"""
import uuid
from typing import AsyncGenerator, Callable, List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User, UserRole, UserStatus

security = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Validate access token and return current authenticated active user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials
    try:
        payload = decode_token(token)
        token_type = payload.get("type")
        if token_type != "access":
            raise credentials_exception
        user_id_str: str = payload.get("sub")
        if not user_id_str:
            raise credentials_exception
        user_id = uuid.UUID(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )
    return user


def require_roles(*allowed_roles: UserRole) -> Callable:
    """Dependency factory to enforce RBAC permissions."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted for role '{current_user.role.value}'",
            )
        return current_user

    return role_checker


def enforce_geo_scope(
    current_user: User,
    district_id: Optional[uuid.UUID] = None,
    taluka_id: Optional[uuid.UUID] = None,
) -> bool:
    """
    Enforces geographic scope:
    - STATE_HEAD: All Karnataka.
    - DISTRICT_ADMIN: Only assigned district.
    - TALUKA_ADMIN: Only assigned taluka.
    """
    if current_user.role == UserRole.STATE_HEAD:
        return True

    if current_user.role == UserRole.DISTRICT_ADMIN:
        if district_id and current_user.district_id != district_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access outside assigned district scope is forbidden",
            )
        return True

    if current_user.role == UserRole.TALUKA_ADMIN:
        if taluka_id and current_user.taluka_id != taluka_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access outside assigned taluka scope is forbidden",
            )
        return True

    return True
