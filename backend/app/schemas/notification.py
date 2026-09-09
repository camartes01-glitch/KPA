"""
Notification Schemas for Multi-Channel Delivery and Scoped Broadcasts.
"""
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.notification import NotificationChannel, NotificationType


class BroadcastCreateRequest(BaseModel):
    title_en: str = Field(..., min_length=3, max_length=255)
    title_kn: str = Field(..., min_length=3, max_length=255)
    body_en: str = Field(..., min_length=5)
    body_kn: str = Field(..., min_length=5)
    district_id: Optional[uuid.UUID] = None
    taluka_id: Optional[uuid.UUID] = None
    channel: NotificationChannel = NotificationChannel.IN_APP
    type: NotificationType = NotificationType.GENERAL_BROADCAST


class NotificationRead(BaseModel):
    id: uuid.UUID
    channel: NotificationChannel
    type: NotificationType
    title: str
    body: str
    is_read: bool
    sent_at: datetime
    district_id: Optional[uuid.UUID] = None
    taluka_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)


class NotificationDetailedRead(BaseModel):
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    district_id: Optional[uuid.UUID] = None
    taluka_id: Optional[uuid.UUID] = None
    channel: NotificationChannel
    type: NotificationType
    title_en: str
    title_kn: str
    body_en: str
    body_kn: str
    is_read: bool
    sent_at: datetime

    model_config = ConfigDict(from_attributes=True)
