"""
Welfare Event and Contribution Models.
Implements mutual relief fund with idempotent ₹10 per-member contributions.
"""
import enum
import uuid
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class WelfareEventStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    DISBURSED = "DISBURSED"


class ContributionStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    EXEMPT = "EXEMPT"


class WelfareEvent(BaseModel):
    """Mutual relief fund event triggered upon demise of a member."""
    __tablename__ = "welfare_events"

    deceased_member_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("members.id"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    death_date: Mapped[date] = mapped_column(Date, nullable=False)
    cause_of_death: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    death_certificate_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    target_amount: Mapped[float] = mapped_column(
        Numeric(12, 2),
        default=0.00,
        nullable=False,
    )
    collected_amount: Mapped[float] = mapped_column(
        Numeric(12, 2),
        default=0.00,
        nullable=False,
    )
    status: Mapped[WelfareEventStatus] = mapped_column(
        SQLEnum(WelfareEventStatus, name="welfare_event_status", native_enum=False),
        default=WelfareEventStatus.ACTIVE,
        nullable=False,
        index=True,
    )
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id"),
        nullable=False,
    )

    # Relationships
    deceased_member: Mapped["Member"] = relationship("Member", foreign_keys=[deceased_member_id])
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])
    contributions: Mapped[List["WelfareContribution"]] = relationship(
        "WelfareContribution",
        back_populates="event",
        cascade="all, delete-orphan",
    )


class WelfareContribution(BaseModel):
    """₹10 mandatory member debit ledger entry for a welfare event."""
    __tablename__ = "welfare_contributions"
    __table_args__ = (
        UniqueConstraint("event_id", "member_id", name="uq_welfare_event_member"),
    )

    event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("welfare_events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    member_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("members.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount: Mapped[float] = mapped_column(
        Numeric(8, 2),
        default=10.00,
        nullable=False,
    )
    status: Mapped[ContributionStatus] = mapped_column(
        SQLEnum(ContributionStatus, name="contribution_status", native_enum=False),
        default=ContributionStatus.PENDING,
        nullable=False,
        index=True,
    )
    payment_method: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    event: Mapped["WelfareEvent"] = relationship("WelfareEvent", back_populates="contributions")
    member: Mapped["Member"] = relationship("Member", foreign_keys=[member_id])
