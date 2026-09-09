"""
Payment Model for Gateway Orders, Webhook Settlements, and Member Receipts.
"""
import enum
import uuid
from typing import Optional

from sqlalchemy import (
    ForeignKey,
    Numeric,
    String,
    Text,
    Uuid,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class PaymentStatus(str, enum.Enum):
    CREATED = "CREATED"
    AUTHORIZED = "AUTHORIZED"
    CAPTURED = "CAPTURED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class Payment(BaseModel):
    """Payment transaction record across UPI, AutoPay, and Gateway."""
    __tablename__ = "payments"

    contribution_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid,
        ForeignKey("welfare_contributions.id"),
        nullable=True,
        index=True,
    )
    member_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("members.id"),
        nullable=False,
        index=True,
    )
    gateway: Mapped[str] = mapped_column(String(20), default="RAZORPAY", nullable=False)
    gateway_order_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )
    gateway_payment_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=True,
    )
    amount: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(String(5), default="INR", nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        SQLEnum(PaymentStatus, name="payment_status", native_enum=False),
        default=PaymentStatus.CREATED,
        nullable=False,
        index=True,
    )
    payment_method: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    receipt_no: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    signature: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    raw_payload: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    contribution: Mapped[Optional["WelfareContribution"]] = relationship("WelfareContribution")
    member: Mapped["Member"] = relationship("Member", foreign_keys=[member_id])
