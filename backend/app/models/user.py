"""
User, OTP Verification, and Device Session models for Authentication & RBAC.
"""
import enum
import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Boolean, DateTime, Integer, Text, ForeignKey, Uuid, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class UserRole(str, enum.Enum):
    STATE_HEAD = "STATE_HEAD"
    DISTRICT_ADMIN = "DISTRICT_ADMIN"
    TALUKA_ADMIN = "TALUKA_ADMIN"
    AUDITOR = "AUDITOR"
    MEMBER = "MEMBER"


class UserStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REJECTED = "REJECTED"


class User(BaseModel):
    """System user representing admins or registered photographers."""
    __tablename__ = "users"

    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, index=True, nullable=True)
    google_sub: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role", native_enum=False),
        default=UserRole.MEMBER,
        nullable=False,
        index=True,
    )
    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(UserStatus, name="user_status", native_enum=False),
        default=UserStatus.PENDING,
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Geographic scoping for RBAC
    district_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid,
        nullable=True,
        index=True,
    )
    taluka_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid,
        nullable=True,
        index=True,
    )

    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    sessions: Mapped[List["DeviceSession"]] = relationship(
        "DeviceSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class OTPVerification(BaseModel):
    """Stores temporary OTP codes with expiry and rate limiting."""
    __tablename__ = "otp_verifications"

    phone: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    otp_code: Mapped[str] = mapped_column(String(100), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class DeviceSession(BaseModel):
    """User device session for refresh token rotation and revocation."""
    __tablename__ = "device_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    refresh_token_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    device_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    device_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="sessions")
