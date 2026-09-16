"""
Test Razorpay Payment Order Creation, Signature Verification, Webhooks, Idempotency, and Receipts.
"""
import hashlib
import hmac
import json
from datetime import date, datetime
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.geo import District, Taluka
from app.models.member import Member, MemberStatus
from app.models.payment import Payment, PaymentStatus
from app.models.user import User, UserRole, UserStatus
from app.models.welfare import ContributionStatus, WelfareContribution, WelfareEvent, WelfareEventStatus
from app.services.payment_service import PaymentService


@pytest.mark.asyncio
async def test_razorpay_signature_verification():
    """Verify HMAC SHA256 signature logic for Razorpay."""
    order_id = "order_test_123"
    payment_id = "pay_test_456"
    secret = settings.RAZORPAY_KEY_SECRET or "dev-secret-key"

    msg = f"{order_id}|{payment_id}".encode("utf-8")
    valid_sig = hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()

    assert PaymentService.verify_razorpay_signature(order_id, payment_id, valid_sig) is True
    assert PaymentService.verify_razorpay_signature(order_id, payment_id, "invalid_signature") is False


@pytest.mark.asyncio
async def test_razorpay_webhook_signature_verification():
    """Verify Razorpay webhook signature header X-Razorpay-Signature."""
    raw_body = b'{"event": "payment.captured", "payload": {}}'
    secret = settings.RAZORPAY_WEBHOOK_SECRET or settings.RAZORPAY_KEY_SECRET or "dev-webhook-secret"

    valid_sig = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    assert PaymentService.verify_webhook_signature(raw_body, valid_sig) is True
    assert PaymentService.verify_webhook_signature(raw_body, "tampered_signature") is False


@pytest.mark.asyncio
async def test_webhook_payment_captured_and_idempotency(client: AsyncClient, db_session: AsyncSession):
    """Test webhook processing of payment.captured with duplicate prevention."""
    # 1. Seed Member and Welfare Event
    district = District(name_en="Bangalore Urban", name_kn="ಬೆಂಗಳೂರು ನಗರ", code="BLR")
    db_session.add(district)
    await db_session.flush()

    taluka = Taluka(district_id=district.id, name_en="Bangalore South", name_kn="ದಕ್ಷಿಣ", code="BLR-S")
    db_session.add(taluka)
    await db_session.flush()

    user = User(
        phone="+919876543210",
        role=UserRole.MEMBER,
        status=UserStatus.ACTIVE,
        district_id=district.id,
    )
    db_session.add(user)
    await db_session.flush()

    member = Member(
        user_id=user.id,
        district_id=district.id,
        taluka_id=taluka.id,
        membership_no="KPA-BLR-0099",
        full_name="Ramesh Kumar",
        gender="MALE",
        dob=date(1985, 5, 15),
        status=MemberStatus.APPROVED,
    )
    db_session.add(member)
    await db_session.flush()

    event = WelfareEvent(
        deceased_member_id=member.id,
        created_by_id=user.id,
        title="Bereavement Benefit",
        death_date=date(2026, 9, 1),
        target_amount=100.0,
        collected_amount=0.0,
        status=WelfareEventStatus.ACTIVE,
    )
    db_session.add(event)
    await db_session.flush()

    contrib = WelfareContribution(
        event_id=event.id,
        member_id=member.id,
        amount=10.0,
        status=ContributionStatus.PENDING,
    )
    db_session.add(contrib)
    await db_session.flush()

    order_id = "order_wh_test_1001"
    payment = Payment(
        contribution_id=contrib.id,
        member_id=member.id,
        gateway="RAZORPAY",
        gateway_order_id=order_id,
        amount=10.0,
        currency="INR",
        status=PaymentStatus.CREATED,
        receipt_no="RCP-20260916-TEST01",
    )
    db_session.add(payment)
    await db_session.commit()

    # 2. Call Webhook with payment.captured
    webhook_payload = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_test_wh_999",
                    "order_id": order_id,
                    "amount": 1000,
                    "currency": "INR",
                    "status": "captured",
                    "method": "upi",
                }
            }
        },
    }
    raw_body = json.dumps(webhook_payload).encode("utf-8")
    secret = settings.RAZORPAY_WEBHOOK_SECRET or settings.RAZORPAY_KEY_SECRET or "dev-webhook-secret"
    signature = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()

    response = await client.post(
        "/api/v1/payments/webhook",
        content=raw_body,
        headers={
            "Content-Type": "application/json",
            "X-Razorpay-Signature": signature,
        },
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "ok"
    assert res_data["result"]["status"] == "settled"

    # Verify payment settled in DB
    await db_session.refresh(payment)
    assert payment.status == PaymentStatus.CAPTURED
    assert payment.gateway_payment_id == "pay_test_wh_999"

    # 3. Test duplicate webhook (Idempotency)
    response_dup = await client.post(
        "/api/v1/payments/webhook",
        content=raw_body,
        headers={
            "Content-Type": "application/json",
            "X-Razorpay-Signature": signature,
        },
    )
    assert response_dup.status_code == 200
    res_dup_data = response_dup.json()
    assert res_dup_data["result"]["status"] == "already_settled"


@pytest.mark.asyncio
async def test_receipts_listing(client: AsyncClient, db_session: AsyncSession):
    """Test paginated receipts listing endpoint."""
    district = District(name_en="Mysore", name_kn="ಮೈಸೂರು", code="MYS")
    db_session.add(district)
    await db_session.flush()

    taluka = Taluka(district_id=district.id, name_en="Mysore City", name_kn="ಮೈಸೂರು", code="MYS-C")
    db_session.add(taluka)
    await db_session.flush()

    user = User(
        phone="+919988776655",
        role=UserRole.STATE_HEAD,
        status=UserStatus.ACTIVE,
    )
    db_session.add(user)
    await db_session.flush()

    member = Member(
        user_id=user.id,
        district_id=district.id,
        taluka_id=taluka.id,
        membership_no="KPA-MYS-0012",
        full_name="Anand Murthy",
        gender="MALE",
        dob=date(1980, 1, 1),
        status=MemberStatus.APPROVED,
    )
    db_session.add(member)
    await db_session.flush()

    receipt_no = "RCP-20260916-MYS01"
    payment = Payment(
        member_id=member.id,
        gateway="RAZORPAY",
        gateway_order_id="order_mys_01",
        gateway_payment_id="pay_mys_01",
        amount=10.0,
        currency="INR",
        status=PaymentStatus.CAPTURED,
        receipt_no=receipt_no,
    )
    db_session.add(payment)
    await db_session.commit()

    # Login / get token for State Head
    from app.core.security import create_access_token
    token = create_access_token(str(user.id), user.role.value)

    res = await client.get(
        "/api/v1/payments/receipts?page=1&page_size=10",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["total"] >= 1
    assert any(r["receipt_no"] == receipt_no for r in body["data"])
