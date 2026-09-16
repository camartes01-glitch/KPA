"""
Authentication Endpoints — OTP login, token refresh, logout, and current user profile.
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_roles
from app.models.user import User, UserRole, UserStatus
from app.schemas.auth import (
    AdminCreateRequest,
    AdminUpdateRequest,
    GoogleAuthRequest,
    RefreshTokenRequest,
    SendOTPRequest,
    TokenResponse,
    UserRead,
    VerifyOTPRequest,
)
from app.schemas.common import APIResponse
from app.services.auth_service import AuthService
from app.services.google_auth_service import GoogleAuthService

router = APIRouter()


@router.post(
    "/google",
    response_model=APIResponse[TokenResponse],
    summary="Authenticate with Google OAuth ID token",
)
async def auth_google(
    payload: GoogleAuthRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Verify submitted Google ID token, provision or link user, create session, and issue JWT tokens."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        tokens = await GoogleAuthService.authenticate_with_google(
            db=db,
            id_token_str=payload.id_token,
            device_name=payload.device_name,
            device_id=payload.device_id,
            ip_address=client_ip,
            user_agent=user_agent,
        )
        return APIResponse(
            success=True,
            message="Authentication successful",
            data=tokens,
        )
    except Exception:
        raise



@router.post(
    "/otp/send",
    response_model=APIResponse[dict],
    summary="Request OTP for mobile authentication",
)
async def send_otp(
    payload: SendOTPRequest,
    db: AsyncSession = Depends(get_db),
):
    """Send a 6-digit OTP code to the given Indian mobile number."""
    result = await AuthService.request_otp(db, payload.phone)
    return APIResponse(
        success=True,
        message="OTP sent successfully",
        data=result,
    )


@router.post(
    "/otp/verify",
    response_model=APIResponse[TokenResponse],
    summary="Verify OTP and receive JWT access + refresh tokens",
)
async def verify_otp(
    payload: VerifyOTPRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Verify submitted OTP code, create device session, and issue JWT tokens."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    tokens = await AuthService.verify_otp(
        db=db,
        phone=payload.phone,
        otp=payload.otp,
        device_name=payload.device_name,
        device_id=payload.device_id,
        ip_address=client_ip,
        user_agent=user_agent,
    )
    return APIResponse(
        success=True,
        message="Authentication successful",
        data=tokens,
    )


@router.post(
    "/token/refresh",
    response_model=APIResponse[TokenResponse],
    summary="Rotate refresh token and get a new access token",
)
async def refresh_token(
    payload: RefreshTokenRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Rotate the refresh token and issue a fresh short-lived access token."""
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    tokens = await AuthService.refresh_access_token(
        db=db,
        refresh_token_str=payload.refresh_token,
        ip_address=client_ip,
        user_agent=user_agent,
    )
    return APIResponse(
        success=True,
        message="Token refreshed successfully",
        data=tokens,
    )


@router.post(
    "/logout",
    response_model=APIResponse[dict],
    summary="Logout and revoke current session",
)
async def logout(
    payload: Optional[RefreshTokenRequest] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke the active device session."""
    refresh_token_val = payload.refresh_token if payload else None
    await AuthService.logout(db, refresh_token_val)
    return APIResponse(
        success=True,
        message="Logged out successfully",
        data={"user_id": str(current_user.id)},
    )


@router.get(
    "/me",
    response_model=APIResponse[UserRead],
    summary="Get authenticated user profile and permissions",
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """Retrieve details of the currently authenticated user."""
    return APIResponse(
        success=True,
        message="Profile retrieved",
        data=UserRead.model_validate(current_user),
    )


@router.get(
    "/admins",
    response_model=APIResponse[List[UserRead]],
    summary="List administrative users (STATE_HEAD & DISTRICT_ADMIN only)",
)
async def list_admins(
    current_user: User = Depends(require_roles(UserRole.STATE_HEAD, UserRole.DISTRICT_ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve list of administrators scoped by jurisdiction."""
    stmt = select(User).where(
        User.role.in_([UserRole.STATE_HEAD, UserRole.DISTRICT_ADMIN, UserRole.TALUKA_ADMIN, UserRole.AUDITOR])
    )
    if current_user.role == UserRole.DISTRICT_ADMIN:
        stmt = stmt.where(User.district_id == current_user.district_id)

    stmt = stmt.order_by(User.role, User.name)
    result = await db.execute(stmt)
    admins = result.scalars().all()
    return APIResponse(
        success=True,
        message="Administrators retrieved",
        data=[UserRead.model_validate(u) for u in admins],
    )


@router.post(
    "/admins",
    response_model=APIResponse[UserRead],
    summary="Create or assign an administrator role",
)
async def create_admin(
    payload: AdminCreateRequest,
    current_user: User = Depends(require_roles(UserRole.STATE_HEAD, UserRole.DISTRICT_ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Create an administrator with geographic scoping."""
    # RBAC rules
    if current_user.role == UserRole.DISTRICT_ADMIN:
        if payload.role != UserRole.TALUKA_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="District Admins may only create Taluka Administrators within their own district.",
            )
        payload.district_id = current_user.district_id

    # Validate geographic assignment
    if payload.role in (UserRole.DISTRICT_ADMIN, UserRole.TALUKA_ADMIN) and not payload.district_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="District ID is required for district and taluka administrators.",
        )

    # Check if user with phone already exists
    stmt = select(User).where(User.phone == payload.phone)
    existing = (await db.execute(stmt)).scalar_one_or_none()

    if existing:
        existing.name = payload.name or existing.name
        existing.email = payload.email or existing.email
        existing.role = payload.role
        existing.district_id = payload.district_id
        existing.taluka_id = payload.taluka_id
        existing.status = UserStatus.ACTIVE
        existing.is_active = True
        user_to_save = existing
    else:
        user_to_save = User(
            phone=payload.phone,
            name=payload.name,
            email=payload.email,
            role=payload.role,
            status=UserStatus.ACTIVE,
            is_active=True,
            district_id=payload.district_id,
            taluka_id=payload.taluka_id,
        )
        db.add(user_to_save)

    await db.commit()
    await db.refresh(user_to_save)

    from app.services.audit_service import AuditService
    await AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="ADMIN_CREATE",
        resource_type="User",
        resource_id=str(user_to_save.id),
        payload={"role": payload.role.value, "phone": payload.phone, "district_id": str(payload.district_id) if payload.district_id else None},
    )

    return APIResponse(
        success=True,
        message="Administrator assigned successfully",
        data=UserRead.model_validate(user_to_save),
    )


@router.patch(
    "/admins/{admin_id}",
    response_model=APIResponse[UserRead],
    summary="Update administrator role, status, or jurisdiction",
)
async def update_admin(
    admin_id: uuid.UUID,
    payload: AdminUpdateRequest,
    current_user: User = Depends(require_roles(UserRole.STATE_HEAD, UserRole.DISTRICT_ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Update administrator details, activation, and jurisdictions."""
    stmt = select(User).where(User.id == admin_id)
    admin = (await db.execute(stmt)).scalar_one_or_none()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Administrator not found.",
        )

    # Scoping check for DISTRICT_ADMIN
    if current_user.role == UserRole.DISTRICT_ADMIN:
        if admin.district_id != current_user.district_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only manage administrators in your own district.",
            )
        if payload.role and payload.role != UserRole.TALUKA_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot promote administrators above Taluka Admin.",
            )

    if payload.name is not None:
        admin.name = payload.name
    if payload.email is not None:
        admin.email = payload.email
    if payload.role is not None:
        admin.role = payload.role
    if payload.is_active is not None:
        admin.is_active = payload.is_active
    if payload.status is not None:
        admin.status = payload.status
    if payload.district_id is not None:
        admin.district_id = payload.district_id
    if payload.taluka_id is not None:
        admin.taluka_id = payload.taluka_id

    await db.commit()
    await db.refresh(admin)

    from app.services.audit_service import AuditService
    await AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="ADMIN_UPDATE",
        resource_type="User",
        resource_id=str(admin.id),
        payload={"is_active": admin.is_active, "role": admin.role.value},
    )

    return APIResponse(
        success=True,
        message="Administrator updated successfully",
        data=UserRead.model_validate(admin),
    )
