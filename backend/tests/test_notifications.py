"""
Tests for Notification Service — Multi-Channel, Bilingual English/Kannada, and Scoped Broadcasts.
"""
from datetime import date
import uuid
import pytest
from app.core.security import create_access_token
from app.models.notification import NotificationChannel, NotificationType
from app.models.user import User, UserRole, UserStatus
from app.services.geo_service import GeoService
from app.services.notification_service import NotificationService


@pytest.mark.asyncio
async def test_user_personal_notification_bilingual(client, db_session):
    """Test notification retrieval in English and Kannada languages."""
    user = User(
        phone="+919876588001",
        name="Laxman Photographer",
        role=UserRole.MEMBER,
        status=UserStatus.ACTIVE,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    token = create_access_token(subject=str(user.id), role=user.role.value)

    # Send notification
    notif = await NotificationService.send_user_notification(
        db=db_session,
        user_id=user.id,
        title_en="ID Card Ready",
        title_kn="ಗುರುತಿನ ಚೀಟಿ ಸಿದ್ಧವಾಗಿದೆ",
        body_en="Your digital membership ID card has been issued.",
        body_kn="ನಿಮ್ಮ ಡಿಜಿಟಲ್ ಸದಸ್ಯತ್ವ ಗುರುತಿನ ಚೀಟಿಯನ್ನು ನೀಡಲಾಗಿದೆ.",
        notification_type=NotificationType.KYC_UPDATE,
        channel=NotificationChannel.IN_APP,
    )

    # 1. Fetch in English
    res_en = await client.get(
        "/api/v1/notifications/my?lang=en",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_en.status_code == 200
    items_en = res_en.json()["data"]
    assert len(items_en) == 1
    assert items_en[0]["title"] == "ID Card Ready"
    assert "digital membership" in items_en[0]["body"]
    assert items_en[0]["is_read"] is False

    # 2. Fetch in Kannada
    res_kn = await client.get(
        "/api/v1/notifications/my?lang=kn",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_kn.status_code == 200
    items_kn = res_kn.json()["data"]
    assert len(items_kn) == 1
    assert "ಗುರುತಿನ ಚೀಟಿ" in items_kn[0]["title"]

    # 3. Mark as read
    read_res = await client.post(
        f"/api/v1/notifications/{notif.id}/read",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert read_res.status_code == 200

    # 4. Verify marked read
    res_check = await client.get(
        "/api/v1/notifications/my",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_check.json()["data"][0]["is_read"] is True


@pytest.mark.asyncio
async def test_scoped_broadcast_notification(client, db_session):
    """Test broadcast targeting specific district scope."""
    await GeoService.seed_karnataka_data(db_session)
    districts = await GeoService.get_all_districts(db_session)
    blr_dist = next(d for d in districts if d.code == "BLR_U")
    mys_dist = next(d for d in districts if d.code == "MYS")

    admin = User(
        phone="+919876588099",
        name="Leader",
        role=UserRole.STATE_HEAD,
        status=UserStatus.ACTIVE,
        is_active=True,
    )
    blr_user = User(
        phone="+919876588010",
        name="Bengaluru Member",
        role=UserRole.MEMBER,
        status=UserStatus.ACTIVE,
        district_id=blr_dist.id,
        is_active=True,
    )
    mys_user = User(
        phone="+919876588020",
        name="Mysuru Member",
        role=UserRole.MEMBER,
        status=UserStatus.ACTIVE,
        district_id=mys_dist.id,
        is_active=True,
    )
    db_session.add_all([admin, blr_user, mys_user])
    await db_session.commit()

    admin_token = create_access_token(subject=str(admin.id), role=admin.role.value)
    blr_token = create_access_token(subject=str(blr_user.id), role=blr_user.role.value)
    mys_token = create_access_token(subject=str(mys_user.id), role=mys_user.role.value)

    # Broadcast targeting only Bengaluru Urban
    broadcast_res = await client.post(
        "/api/v1/notifications/broadcast",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title_en": "Bengaluru General Meeting",
            "title_kn": "ಬೆಂಗಳೂರು ಸಾಮಾನ್ಯ ಸಭೆ",
            "body_en": "Meeting scheduled for all Bengaluru members on Sunday.",
            "body_kn": "ಭಾನುವಾರ ಎಲ್ಲಾ ಬೆಂಗಳೂರು ಸದಸ್ಯರಿಗೆ ಸಭೆಯನ್ನು ನಿಗದಿಪಡಿಸಲಾಗಿದೆ.",
            "district_id": str(blr_dist.id),
        },
    )
    assert broadcast_res.status_code == 200

    # Bengaluru user should receive it
    blr_feed = await client.get("/api/v1/notifications/my", headers={"Authorization": f"Bearer {blr_token}"})
    assert len(blr_feed.json()["data"]) == 1
    assert blr_feed.json()["data"][0]["title"] == "Bengaluru General Meeting"

    # Mysuru user should NOT receive it
    mys_feed = await client.get("/api/v1/notifications/my", headers={"Authorization": f"Bearer {mys_token}"})
    assert len(mys_feed.json()["data"]) == 0
