"""
Settings Endpoints — Association Profile, Welfare Rules, and Integration Health.
"""
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_roles
from app.core.config import settings
from app.models.user import User, UserRole
from app.schemas.common import APIResponse
from app.services.audit_service import AuditService

router = APIRouter()

# In-memory runtime configuration overrides
_runtime_settings: Dict[str, Any] = {
    "association_name": "Karnataka Photography Association (Regd.)",
    "association_name_kn": "ಕರ್ನಾಟಕ ಛಾಯಾಗ್ರಾಹಕರ ಸಂಘ (ರಿ.)",
    "association_address": "Bengaluru, Karnataka, India",
    "contact_phone": "+91 80 2233 4455",
    "contact_email": "support@kpawelfare.org",
    "welfare_contribution_inr": 10.0,
    "welfare_grace_days": 14,
}


class SettingsUpdateRequest(BaseModel):
    association_name: Optional[str] = None
    association_name_kn: Optional[str] = None
    association_address: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    welfare_contribution_inr: Optional[float] = None
    welfare_grace_days: Optional[int] = None


@router.get(
    "",
    summary="Get platform settings and integration provider statuses",
)
async def get_settings(
    current_user: User = Depends(get_current_user),
):
    """Retrieve system configuration and integration health indicators (no secrets exposed)."""
    return APIResponse(
        success=True,
        message="Settings retrieved",
        data={
            **_runtime_settings,
            "providers": {
                "razorpay_configured": bool(settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET),
                "sms_configured": bool(settings.MSG91_AUTH_KEY),
                "email_configured": bool(settings.SENDGRID_API_KEY or settings.RESEND_API_KEY or settings.SMTP_HOST),
                "push_configured": bool(settings.FIREBASE_SERVICE_ACCOUNT_JSON or settings.FIREBASE_SERVICE_ACCOUNT_PATH),
            },
            "security": {
                "jwt_access_expire_minutes": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
                "jwt_refresh_expire_days": settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS,
                "otp_expiry_minutes": settings.OTP_EXPIRY_MINUTES,
                "otp_dev_mode": settings.OTP_DEV_MODE,
                "app_env": settings.APP_ENV,
            },
        },
    )


@router.patch(
    "",
    summary="Update platform settings (State Head only)",
)
async def update_settings(
    payload: SettingsUpdateRequest,
    current_user: User = Depends(require_roles(UserRole.STATE_HEAD)),
    db: AsyncSession = Depends(get_db),
):
    """Update global platform configuration with full audit logging."""
    updated = {}
    if payload.association_name is not None:
        _runtime_settings["association_name"] = payload.association_name
        updated["association_name"] = payload.association_name
    if payload.association_name_kn is not None:
        _runtime_settings["association_name_kn"] = payload.association_name_kn
        updated["association_name_kn"] = payload.association_name_kn
    if payload.association_address is not None:
        _runtime_settings["association_address"] = payload.association_address
        updated["association_address"] = payload.association_address
    if payload.contact_phone is not None:
        _runtime_settings["contact_phone"] = payload.contact_phone
        updated["contact_phone"] = payload.contact_phone
    if payload.contact_email is not None:
        _runtime_settings["contact_email"] = payload.contact_email
        updated["contact_email"] = payload.contact_email
    if payload.welfare_contribution_inr is not None:
        if payload.welfare_contribution_inr <= 0:
            raise HTTPException(status_code=400, detail="Contribution amount must be positive")
        _runtime_settings["welfare_contribution_inr"] = payload.welfare_contribution_inr
        updated["welfare_contribution_inr"] = payload.welfare_contribution_inr
    if payload.welfare_grace_days is not None:
        if payload.welfare_grace_days < 1:
            raise HTTPException(status_code=400, detail="Grace days must be at least 1")
        _runtime_settings["welfare_grace_days"] = payload.welfare_grace_days
        updated["welfare_grace_days"] = payload.welfare_grace_days

    await AuditService.log_action(
        db=db,
        action="UPDATE_PLATFORM_SETTINGS",
        resource_type="SETTINGS",
        user_id=current_user.id,
        payload=updated,
    )

    return APIResponse(
        success=True,
        message="Settings updated successfully",
        data=_runtime_settings,
    )
