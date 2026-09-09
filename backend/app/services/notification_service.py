"""
Notification Service — Multi-Channel Delivery, Scoped Geographic Broadcasts, and Localization.
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import enforce_geo_scope
from app.models.notification import Notification, NotificationChannel, NotificationType
from app.models.user import User, UserRole
from app.schemas.notification import BroadcastCreateRequest, NotificationRead


class NotificationService:
    @staticmethod
    async def send_user_notification(
        db: AsyncSession,
        user_id: uuid.UUID,
        title_en: str,
        title_kn: str,
        body_en: str,
        body_kn: str,
        notification_type: NotificationType = NotificationType.GENERAL_BROADCAST,
        channel: NotificationChannel = NotificationChannel.IN_APP,
        metadata_json: Optional[str] = None,
    ) -> Notification:
        """Deliver targeted notification to a specific user account."""
        now = datetime.now(timezone.utc)
        notif = Notification(
            user_id=user_id,
            channel=channel,
            type=notification_type,
            title_en=title_en,
            title_kn=title_kn,
            body_en=body_en,
            body_kn=body_kn,
            is_read=False,
            sent_at=now,
            metadata_json=metadata_json,
        )
        db.add(notif)
        await db.commit()
        await db.refresh(notif)
        return notif

    @staticmethod
    async def broadcast_notification(
        db: AsyncSession,
        sender: User,
        data: BroadcastCreateRequest,
    ) -> Notification:
        """Send scoped announcement to association members."""
        # Enforce geographic scoping
        enforce_geo_scope(sender, district_id=data.district_id, taluka_id=data.taluka_id)

        now = datetime.now(timezone.utc)
        notif = Notification(
            district_id=data.district_id,
            taluka_id=data.taluka_id,
            channel=data.channel,
            type=data.type,
            title_en=data.title_en,
            title_kn=data.title_kn,
            body_en=data.body_en,
            body_kn=data.body_kn,
            is_read=False,
            sent_at=now,
        )
        db.add(notif)
        await db.commit()
        await db.refresh(notif)
        return notif

    @staticmethod
    async def get_user_notifications(
        db: AsyncSession,
        user: User,
        lang: str = "en",
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[NotificationRead], int]:
        """Fetch notifications relevant to the user: personal + scoped broadcasts."""
        # Condition: assigned to user OR broadcast matching user's location
        conditions = [Notification.user_id == user.id]

        broadcast_filter = Notification.user_id == None  # noqa: E711
        if user.district_id:
            broadcast_filter = broadcast_filter & or_(
                Notification.district_id == None,  # noqa: E711
                Notification.district_id == user.district_id,
            )
        if user.taluka_id:
            broadcast_filter = broadcast_filter & or_(
                Notification.taluka_id == None,  # noqa: E711
                Notification.taluka_id == user.taluka_id,
            )

        conditions.append(broadcast_filter)

        stmt = select(Notification).where(or_(*conditions))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar() or 0

        stmt = stmt.order_by(Notification.sent_at.desc()).offset((page - 1) * page_size).limit(page_size)
        notifs = (await db.execute(stmt)).scalars().all()

        results = []
        for n in notifs:
            title = n.title_kn if lang == "kn" else n.title_en
            body = n.body_kn if lang == "kn" else n.body_en
            results.append(
                NotificationRead(
                    id=n.id,
                    channel=n.channel,
                    type=n.type,
                    title=title,
                    body=body,
                    is_read=n.is_read,
                    sent_at=n.sent_at,
                    district_id=n.district_id,
                    taluka_id=n.taluka_id,
                )
            )

        return results, total

    @staticmethod
    async def mark_as_read(
        db: AsyncSession,
        notification_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """Mark a notification as read."""
        notif = await db.get(Notification, notification_id)
        if not notif:
            raise HTTPException(status_code=404, detail="Notification not found")

        notif.is_read = True
        await db.commit()
        return True
