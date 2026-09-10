"""
Authentication schemas for request validation and response formatting.
"""
import re
import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.models.user import UserRole, UserStatus


class SendOTPRequest(BaseModel):
    phone: str = Field(..., description="Indian mobile number (10 digits or with +91)")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        # Normalize: strip spaces, dashes, leading zeros
        cleaned = re.sub(r"[\s\-\(\)]", "", v)
        if cleaned.startswith("+91"):
            cleaned = cleaned[3:]
        elif cleaned.startswith("91") and len(cleaned) == 12:
            cleaned = cleaned[2:]
        elif cleaned.startswith("0") and len(cleaned) == 11:
            cleaned = cleaned[1:]

        if not re.match(r"^[6-9]\d{9}$", cleaned):
            raise ValueError("Must be a valid 10-digit Indian mobile number starting with 6, 7, 8, or 9")
        return f"+91{cleaned}"


class VerifyOTPRequest(BaseModel):
    phone: str = Field(..., description="Phone number that received OTP")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")
    device_name: Optional[str] = None
    device_id: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = re.sub(r"[\s\-\(\)]", "", v)
        if cleaned.startswith("+91"):
            cleaned = cleaned[3:]
        elif cleaned.startswith("91") and len(cleaned) == 12:
            cleaned = cleaned[2:]
        elif cleaned.startswith("0") and len(cleaned) == 11:
            cleaned = cleaned[1:]

        if not re.match(r"^[6-9]\d{9}$", cleaned):
            raise ValueError("Invalid phone format")
        return f"+91{cleaned}"

    @field_validator("otp")
    @classmethod
    def validate_otp(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 6:
            raise ValueError("OTP must be exactly 6 digits")
        return v


class GoogleAuthRequest(BaseModel):
    id_token: str = Field(..., description="Google OAuth2 ID token from Google Identity Services")
    device_name: Optional[str] = None
    device_id: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="JWT refresh token")


class UserRead(BaseModel):
    id: uuid.UUID
    phone: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    role: UserRole
    status: UserStatus
    is_active: bool
    district_id: Optional[uuid.UUID] = None
    taluka_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserRead
