"""
Notification Service — Multi-Channel Delivery (In-App, Push, SMS, Email),
Scoped Geographic Broadcasts, Provider Abstractions, and Bilingual Localization.
"""
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import httpx
from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import enforce_geo_scope
from app.core.config import settings
from app.models.member import Member
from app.models.notification import Notification, NotificationChannel, NotificationType
from app.models.user import User, UserRole
from app.schemas.notification import BroadcastCreateRequest, NotificationRead
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class NotificationProviders:
    @staticmethod
    async def send_push_notification(push_tokens: List[str], title: str, body: str, data: Optional[Dict[str, Any]] = None) -> bool:
        """Send push notification to Expo/FCM push tokens."""
        if not push_tokens:
            return True

        # Expo Push Notification API
        expo_tokens = [t for t in push_tokens if t.startswith("ExponentPushToken")]
        if expo_tokens:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    messages = [
                        {
                            "to": t,
                            "sound": "default",
                            "title": title,
                            "body": body,
                            "data": data or {},
                        }
                        for t in expo_tokens
                    ]
                    resp = await client.post("https://exp.host/--/api/v2/push/send", json=messages)
                    logger.info(f"Expo push sent to {len(expo_tokens)} devices: status {resp.status_code}")
                    return resp.status_code == 200
            except Exception as e:
                logger.error(f"Error sending Expo push notification: {e}")
                return False

        logger.info(f"[DEV PUSH] Broadcast push '{title}': '{body}' to {len(push_tokens)} tokens")
        return True

    @staticmethod
    async def send_sms(phone: str, message: str, template_id: Optional[str] = None) -> bool:
        """Send transactional SMS via MSG91 flow API or standard gateway."""
        if settings.MSG91_AUTH_KEY and template_id:
            try:
                clean_phone = phone.replace("+", "").strip()
                async with httpx.AsyncClient(timeout=10.0) as client:
                    payload = {
                        "template_id": template_id,
                        "short_url": "1",
                        "recipients": [{"mobiles": clean_phone, "message": message}],
                    }
                    resp = await client.post(
                        "https://control.msg91.com/api/v5/flow/",
                        headers={"authkey": settings.MSG91_AUTH_KEY, "content-type": "application/json"},
                        json=payload,
                    )
                    logger.info(f"MSG91 SMS dispatched to {clean_phone}: status {resp.status_code}")
                    return resp.status_code == 200
            except Exception as e:
                logger.error(f"Error sending MSG91 SMS: {e}")
                return False

        logger.info(f"[DEV SMS] To {phone}: {message}")
        return True

    @staticmethod
    async def send_email(to_email: str, subject: str, body: str, is_html: bool = False) -> bool:
        """Send email via SendGrid or Resend API."""
        if settings.SENDGRID_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    payload = {
                        "personalizations": [{"to": [{"email": to_email}]}],
                        "from": {"email": settings.EMAIL_FROM_ADDRESS, "name": settings.EMAIL_FROM_NAME},
                        "subject": subject,
                        "content": [{"type": "text/html" if is_html else "text/plain", "value": body}],
                    }
                    resp = await client.post(
                        "https://api.sendgrid.com/v3/mail/send",
                        headers={"Authorization": f"Bearer {settings.SENDGRID_API_KEY}", "Content-Type": "application/json"},
                        json=payload,
                    )
                    logger.info(f"SendGrid email dispatched to {to_email}: status {resp.status_code}")
                    return resp.status_code in (200, 202)
            except Exception as e:
                logger.error(f"Error sending SendGrid email: {e}")
                return False

        logger.info(f"[DEV EMAIL] To {to_email} - Subject: {subject}")
        return True


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
        """Deliver targeted notification to a specific user account across specified channel."""
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

        # Dispatch via external provider if not solely in-app
        user = await db.get(User, user_id)
        if user:
            if channel == NotificationChannel.SMS and user.phone:
                await NotificationProviders.send_sms(user.phone, f"{title_en}: {body_en}")
            elif channel == NotificationChannel.EMAIL and user.email:
                await NotificationProviders.send_email(user.email, title_en, body_en)

        return notif

    @staticmethod
    async def broadcast_notification(
        db: AsyncSession,
        sender: User,
        data: BroadcastCreateRequest,
    ) -> Notification:
        """Send scoped announcement to association members with geographic isolation and audit log."""
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

        # Audit administrative broadcast
        await AuditService.log_action(
            db=db,
            action="BROADCAST_NOTIFICATION",
            resource_type="NOTIFICATION",
            resource_id=str(notif.id),
            user_id=sender.id,
            payload={
                "channel": data.channel.value,
                "type": data.type.value,
                "title_en": data.title_en,
                "district_id": str(data.district_id) if data.district_id else None,
                "taluka_id": str(data.taluka_id) if data.taluka_id else None,
            },
        )

        return notif

    @staticmethod
    async def trigger_welfare_event_notification(
        db: AsyncSession,
        event: Any,
        deceased_member: Member,
    ) -> Notification:
        """Automatically create and dispatch bilingual statewide notification when a welfare event is declared."""
        now = datetime.now(timezone.utc)
        name = deceased_member.full_name
        title_en = f"Welfare Mutual Fund: Relief Case for {name}"
        title_kn = f"ಕ್ಷೇಮಾಭಿವೃದ್ಧಿ ಪರಸ್ಪರ ನಿಧಿ: {name} ಅವರಿಗೆ ಪರಿಹಾರ ಪ್ರಕರಣ"

        body_en = (
            f"A statutory mutual relief contribution of ₹10 has been debited to support the family of our beloved member {name} "
            f"(Membership ID: {deceased_member.membership_no or 'N/A'}). Please review case details in your Welfare tab."
        )
        body_kn = (
            f"ನಮ್ಮ ಪ್ರೀತಿಯ ಸದಸ್ಯರಾದ {name} ಅವರ ನಿಧನದ ಹಿನ್ನೆಲೆಯಲ್ಲಿ ಅವರ ಕುಟುಂಬದ ನೆರವಿಗಾಗಿ ₹10 ರ ಪರಸ್ಪರ ಪರಿಹಾರ ಯೋಜನೆಯನ್ನು "
            f"ಘೋಷಿಸಲಾಗಿದೆ. ದಯವಿಟ್ಟು ಕ್ಷೇಮಾಭಿವೃದ್ಧಿ ವಿಭಾಗದಲ್ಲಿ ವಿವರಗಳನ್ನು ಪರಿಶೀಲಿಸಿ."
        )

        notif = Notification(
            district_id=None,  # Statewide scope
            taluka_id=None,
            channel=NotificationChannel.IN_APP,
            type=NotificationType.WELFARE_ALERT,
            title_en=title_en,
            title_kn=title_kn,
            body_en=body_en,
            body_kn=body_kn,
            is_read=False,
            sent_at=now,
            metadata_json=json.dumps({"event_id": str(event.id), "deceased_member_id": str(deceased_member.id)}),
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
