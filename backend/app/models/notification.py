"""
Notification Model for Multi-Channel In-App, Push, SMS, and Scoped Broadcasts.
Supports bilingual Kannada and English templates.
"""
import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
    Uuid,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class NotificationChannel(str, enum.Enum):
    IN_APP = "IN_APP"
    PUSH = "PUSH"
    SMS = "SMS"
    EMAIL = "EMAIL"


class NotificationType(str, enum.Enum):
    WELFARE_ALERT = "WELFARE_ALERT"
    PAYMENT_RECEIPT = "PAYMENT_RECEIPT"
    KYC_UPDATE = "KYC_UPDATE"
    GENERAL_BROADCAST = "GENERAL_BROADCAST"


class Notification(BaseModel):
    """Notification message record with bilingual content and targeting scope."""
    __tablename__ = "notifications"

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    district_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid,
        ForeignKey("districts.id"),
        nullable=True,
        index=True,
    )
    taluka_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid,
        ForeignKey("talukas.id"),
        nullable=True,
        index=True,
    )
    channel: Mapped[NotificationChannel] = mapped_column(
        SQLEnum(NotificationChannel, name="notification_channel", native_enum=False),
        default=NotificationChannel.IN_APP,
        nullable=False,
    )
    type: Mapped[NotificationType] = mapped_column(
        SQLEnum(NotificationType, name="notification_type", native_enum=False),
        default=NotificationType.GENERAL_BROADCAST,
        nullable=False,
    )
    title_en: Mapped[str] = mapped_column(String(255), nullable=False)
    title_kn: Mapped[str] = mapped_column(String(255), nullable=False)
    body_en: Mapped[str] = mapped_column(Text, nullable=False)
    body_kn: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped[Optional["User"]] = relationship("User")
