"""
Authentication Endpoints — OTP login, token refresh, logout, and current user profile.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import RefreshTokenRequest, SendOTPRequest, TokenResponse, UserRead, VerifyOTPRequest
from app.schemas.common import APIResponse
from app.services.auth_service import AuthService

router = APIRouter()


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
