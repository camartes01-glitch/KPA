"""
Tests for Payment Gateway Integration — Order Creation, Signature Verification, and Settlement.
"""
from datetime import date
import uuid
import pytest
from app.core.security import create_access_token
from app.models.member import Member, MemberStatus
from app.models.payment import PaymentStatus
from app.models.user import User, UserRole, UserStatus
from app.models.welfare import ContributionStatus, WelfareContribution, WelfareEvent, WelfareEventStatus
from app.services.geo_service import GeoService


@pytest.mark.asyncio
async def test_payment_flow(client, db_session):
    """Test full payment lifecycle: order creation -> HMAC verification -> settlement."""
    # 1. Seed geo
    await GeoService.seed_karnataka_data(db_session)
    dist = (await GeoService.get_all_districts(db_session))[0]
    taluka = (await GeoService.get_talukas_by_district(db_session, dist.id))[0]

    # 2. Setup user and member
    user = User(
        phone="+919876543299",
        name="Paying Member",
        role=UserRole.MEMBER,
        status=UserStatus.ACTIVE,
        is_active=True,
    )
    admin = User(
        phone="+919876543200",
        name="State Leader",
        role=UserRole.STATE_HEAD,
        status=UserStatus.ACTIVE,
        is_active=True,
    )
    db_session.add_all([user, admin])
    await db_session.flush()

    member = Member(
        user_id=user.id,
        membership_no="KPA-BLRU-00100",
        full_name="Paying Member Suresh",
        gender="MALE",
        dob=date(1990, 1, 1),
        district_id=dist.id,
        taluka_id=taluka.id,
        status=MemberStatus.APPROVED,
    )
    db_session.add(member)
    await db_session.flush()

    # 3. Setup welfare event & pending contribution
    event = WelfareEvent(
        deceased_member_id=member.id,  # for test fixture simplicity
        title="Welfare Relief Benefit Test",
        death_date=date(2026, 8, 1),
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

    token = create_access_token(subject=str(user.id), role=user.role.value)

    # 4. Create payment order
    order_res = await client.post(
        "/api/v1/payments/create-order",
        headers={"Authorization": f"Bearer {token}"},
        json={"contribution_id": str(contrib.id)},
    )
    assert order_res.status_code == 200
    order_data = order_res.json()["data"]
    assert order_data["amount"] == 10.0
    assert order_data["amount_paise"] == 1000
    assert order_data["currency"] == "INR"
    order_id = order_data["order_id"]
    receipt_no = order_data["receipt_no"]

    # 5. Verify payment with valid signature
    verify_res = await client.post(
        "/api/v1/payments/verify",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "gateway_order_id": order_id,
            "gateway_payment_id": "pay_test_12345678",
            "signature": "mock-valid-signature",
        },
    )
    assert verify_res.status_code == 200
    settled_data = verify_res.json()["data"]
    assert settled_data["status"] == "CAPTURED"
    assert settled_data["amount"] == 10.0
    assert settled_data["receipt_no"] == receipt_no
    assert settled_data["member_name"] == "Paying Member Suresh"

    # 6. Retrieve official receipt
    receipt_res = await client.get(f"/api/v1/payments/receipt/{receipt_no}")
    assert receipt_res.status_code == 200
    receipt_data = receipt_res.json()["data"]
    assert receipt_data["receipt_no"] == receipt_no
    assert receipt_data["status"] == "CAPTURED"
