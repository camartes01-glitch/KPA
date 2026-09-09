"""
Member and Nominee models for Photography Association Registration & Digital Cards.
"""
import enum
import uuid
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, Uuid, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class MemberStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUSPENDED = "SUSPENDED"


class Member(BaseModel):
    """Photographer association member record."""
    __tablename__ = "members"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    membership_no: Mapped[Optional[str]] = mapped_column(
        String(30),
        unique=True,
        index=True,
        nullable=True,
    )
    full_name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    father_or_spouse_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    dob: Mapped[date] = mapped_column(Date, nullable=False)
    blood_group: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # Professional details
    studio_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    experience_years: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    photo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    id_card_qr_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Address and jurisdiction
    address_line: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pincode: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    district_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("districts.id"),
        nullable=False,
        index=True,
    )
    taluka_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("talukas.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[MemberStatus] = mapped_column(
        SQLEnum(MemberStatus, name="member_status", native_enum=False),
        default=MemberStatus.PENDING,
        nullable=False,
        index=True,
    )
    approved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid,
        ForeignKey("users.id"),
        nullable=True,
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    district: Mapped["District"] = relationship("District", foreign_keys=[district_id])
    taluka: Mapped["Taluka"] = relationship("Taluka", foreign_keys=[taluka_id])
    nominees: Mapped[List["Nominee"]] = relationship(
        "Nominee",
        back_populates="member",
        cascade="all, delete-orphan",
    )


class Nominee(BaseModel):
    """Member nominee / beneficiary for welfare mutual relief distribution."""
    __tablename__ = "nominees"

    member_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("members.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    relationship_to_member: Mapped[str] = mapped_column(String(50), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    dob: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    aadhaar_last_4: Mapped[Optional[str]] = mapped_column(String(4), nullable=True)
    bank_account_no: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    bank_ifsc: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    bank_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    member: Mapped["Member"] = relationship("Member", back_populates="nominees")
