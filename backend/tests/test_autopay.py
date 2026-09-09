"""
Tests for AutoPay — Mandate Registration, Activation, and Automated Batch Deductions.
"""
from datetime import date
import uuid
import pytest
from app.core.security import create_access_token
from app.models.autopay import MandateStatus
from app.models.member import Member, MemberStatus
from app.models.user import User, UserRole, UserStatus
from app.models.welfare import ContributionStatus, WelfareContribution, WelfareEvent, WelfareEventStatus
from app.services.geo_service import GeoService


@pytest.mark.asyncio
async def test_autopay_mandate_lifecycle(client, db_session):
    """Test mandate creation, activation, and cancellation."""
    await GeoService.seed_karnataka_data(db_session)
    dist = (await GeoService.get_all_districts(db_session))[0]
    taluka = (await GeoService.get_talukas_by_district(db_session, dist.id))[0]

    user = User(
        phone="+919876599001",
        name="AutoPay User",
        role=UserRole.MEMBER,
        status=UserStatus.ACTIVE,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    member = Member(
        user_id=user.id,
        membership_no="KPA-BLRU-00500",
        full_name="AutoPay Member",
        gender="MALE",
        dob=date(1992, 4, 10),
        district_id=dist.id,
        taluka_id=taluka.id,
        status=MemberStatus.APPROVED,
    )
    db_session.add(member)
    await db_session.commit()

    token = create_access_token(subject=str(user.id), role=user.role.value)

    # 1. Create mandate
    create_res = await client.post(
        "/api/v1/autopay/mandate/create",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "auth_type": "UPI",
            "max_amount": 500.00,
            "vpa": "autopay@upi",
            "bank_name": "HDFC Bank",
        },
    )
    assert create_res.status_code == 200
    mandate_data = create_res.json()["data"]
    assert mandate_data["status"] == "CREATED"
    mandate_gateway_id = mandate_data["gateway_mandate_id"]
    mandate_id = mandate_data["id"]

    # 2. Activate mandate
    activate_res = await client.post(
        "/api/v1/autopay/mandate/activate",
        headers={"Authorization": f"Bearer {token}"},
        json={"gateway_mandate_id": mandate_gateway_id},
    )
    assert activate_res.status_code == 200
    assert activate_res.json()["data"]["status"] == "ACTIVE"

    # 3. Query active mandate
    my_mandate_res = await client.get(
        "/api/v1/autopay/my-mandate",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert my_mandate_res.status_code == 200
    assert my_mandate_res.json()["data"]["status"] == "ACTIVE"

    # 4. Cancel mandate
    cancel_res = await client.post(
        f"/api/v1/autopay/mandate/{mandate_id}/cancel",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert cancel_res.status_code == 200
    assert cancel_res.json()["data"]["status"] == "CANCELLED"


@pytest.mark.asyncio
async def test_batch_recurring_debit(client, db_session):
    """Test automated batch debit for welfare event obligations."""
    await GeoService.seed_karnataka_data(db_session)
    dist = (await GeoService.get_all_districts(db_session))[0]
    taluka = (await GeoService.get_talukas_by_district(db_session, dist.id))[0]

    admin = User(
        phone="+919876599099",
        name="State Leader",
        role=UserRole.STATE_HEAD,
        status=UserStatus.ACTIVE,
        is_active=True,
    )
    user = User(
        phone="+919876599002",
        name="AutoPay Subscribed Member",
        role=UserRole.MEMBER,
        status=UserStatus.ACTIVE,
        is_active=True,
    )
    db_session.add_all([admin, user])
    await db_session.flush()

    member = Member(
        user_id=user.id,
        membership_no="KPA-BLRU-00501",
        full_name="AutoPay Member Two",
        gender="MALE",
        dob=date(1991, 1, 1),
        district_id=dist.id,
        taluka_id=taluka.id,
        status=MemberStatus.APPROVED,
    )
    db_session.add(member)
    await db_session.flush()

    # Create & activate mandate
    user_token = create_access_token(subject=str(user.id), role=user.role.value)
    admin_token = create_access_token(subject=str(admin.id), role=admin.role.value)

    c_res = await client.post(
        "/api/v1/autopay/mandate/create",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"auth_type": "UPI", "max_amount": 500.00, "vpa": "member2@upi"},
    )
    mandate_gw_id = c_res.json()["data"]["gateway_mandate_id"]
    await client.post(
        "/api/v1/autopay/mandate/activate",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"gateway_mandate_id": mandate_gw_id},
    )

    # Setup welfare event & pending contribution
    event = WelfareEvent(
        deceased_member_id=member.id,
        title="Batch AutoPay Test Event",
        death_date=date(2026, 8, 2),
        target_amount=10.0,
        collected_amount=0.0,
        status=WelfareEventStatus.ACTIVE,
        created_by_id=admin.id,
    )
    db_session.add(event)
    await db_session.flush()

    contrib = WelfareContribution(
        event_id=event.id,
        member_id=member.id,
        amount=10.00,
        status=ContributionStatus.PENDING,
    )
    db_session.add(contrib)
    await db_session.commit()

    # Trigger batch debit by STATE_HEAD
    batch_res = await client.post(
        f"/api/v1/autopay/batch-debit/{event.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert batch_res.status_code == 200
    summary = batch_res.json()["data"]
    assert summary["debited_count"] == 1
    assert summary["total_amount_debited"] == 10.0

    # Verify contribution settled in DB
    await db_session.refresh(contrib)
    assert contrib.status == ContributionStatus.SUCCESS
    assert contrib.payment_method == "AUTOPAY"
