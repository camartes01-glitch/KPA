"""
AutoPay Mandate Model for Recurring eMandate and UPI AutoPay Registration.
"""
import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Uuid,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class MandateStatus(str, enum.Enum):
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class MandateAuthType(str, enum.Enum):
    UPI = "UPI"
    NETBANKING = "NETBANKING"
    DEBIT_CARD = "DEBIT_CARD"


class AutoPayMandate(BaseModel):
    """Member recurring payment mandate for automatic ₹10 welfare deductions."""
    __tablename__ = "autopay_mandates"

    member_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("members.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    gateway: Mapped[str] = mapped_column(String(20), default="RAZORPAY", nullable=False)
    gateway_mandate_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )
    auth_type: Mapped[MandateAuthType] = mapped_column(
        SQLEnum(MandateAuthType, name="mandate_auth_type", native_enum=False),
        default=MandateAuthType.UPI,
        nullable=False,
    )
    max_amount: Mapped[float] = mapped_column(
        Numeric(8, 2),
        default=500.00,
        nullable=False,
    )
    status: Mapped[MandateStatus] = mapped_column(
        SQLEnum(MandateStatus, name="mandate_status", native_enum=False),
        default=MandateStatus.CREATED,
        nullable=False,
        index=True,
    )
    vpa: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    bank_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    bank_account_last_4: Mapped[Optional[str]] = mapped_column(String(4), nullable=True)
    activated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    member: Mapped["Member"] = relationship("Member")
