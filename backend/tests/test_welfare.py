"""
Tests for Welfare Events & Contributions.
- Idempotent ₹10 contribution batch generation
- RBAC protection (STATE_HEAD only)
- Member obligation querying and payment reconciliation
"""
from datetime import date
import uuid
import pytest
from sqlalchemy import select

from app.core.security import create_access_token
from app.models.geo import District, Taluka
from app.models.member import Member, MemberStatus, Nominee
from app.models.user import User, UserRole, UserStatus
from app.models.welfare import ContributionStatus, WelfareContribution
from app.services.geo_service import GeoService
from app.services.welfare_service import WelfareService


@pytest.mark.asyncio
async def test_welfare_event_creation_and_contributions(client, db_session):
    """Test welfare event creates ₹10 debits for all eligible approved members."""
    # 1. Seed geo
    await GeoService.seed_karnataka_data(db_session)
    dist = (await GeoService.get_all_districts(db_session))[0]
    taluka = (await GeoService.get_talukas_by_district(db_session, dist.id))[0]

    # 2. Setup STATE_HEAD
    admin = User(
        phone="+919999000001",
        name="State Leader",
        role=UserRole.STATE_HEAD,
        status=UserStatus.ACTIVE,
        is_active=True,
    )
    db_session.add(admin)

    # 3. Setup Deceased Member
    deceased_user = User(
        phone="+919999000002",
        name="Late Member",
        role=UserRole.MEMBER,
        status=UserStatus.ACTIVE,
        is_active=True,
    )
    db_session.add(deceased_user)
    await db_session.flush()

    deceased_member = Member(
        user_id=deceased_user.id,
        membership_no="KPA-BLRU-00010",
        full_name="Late Member Ramesh",
        gender="MALE",
        dob=date(1975, 1, 1),
        district_id=dist.id,
        taluka_id=taluka.id,
        status=MemberStatus.APPROVED,
    )
    db_session.add(deceased_member)

    # 4. Setup 3 Active Approved Members
    active_tokens = []
    active_members = []
    for i in range(1, 4):
        u = User(
            phone=f"+91999900001{i}",
            name=f"Active Member {i}",
            role=UserRole.MEMBER,
            status=UserStatus.ACTIVE,
            is_active=True,
        )
        db_session.add(u)
        await db_session.flush()

        m = Member(
            user_id=u.id,
            membership_no=f"KPA-BLRU-0002{i}",
            full_name=f"Active Member {i}",
            gender="MALE",
            dob=date(1985, 2, 2),
            district_id=dist.id,
            taluka_id=taluka.id,
            status=MemberStatus.APPROVED,
        )
        db_session.add(m)
        active_members.append(m)
        active_tokens.append(create_access_token(subject=str(u.id), role=u.role.value))

    await db_session.commit()

    admin_token = create_access_token(subject=str(admin.id), role=admin.role.value)

    # 5. Non-admin attempt must fail with 403 Forbidden
    forbidden_res = await client.post(
        "/api/v1/welfare-events",
        headers={"Authorization": f"Bearer {active_tokens[0]}"},
        json={
            "deceased_member_id": str(deceased_member.id),
            "title": "Emergency Relief for Late Ramesh",
            "death_date": "2026-08-01",
        },
    )
    assert forbidden_res.status_code == 403

    # 6. Admin creates welfare event
    create_res = await client.post(
        "/api/v1/welfare-events",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "deceased_member_id": str(deceased_member.id),
            "title": "Emergency Relief for Late Ramesh",
            "death_date": "2026-08-01",
            "cause_of_death": "Cardiac arrest",
        },
    )
    assert create_res.status_code == 200
    event_data = create_res.json()["data"]
    assert event_data["title"] == "Emergency Relief for Late Ramesh"
    # Target amount should be 3 active members * 10.0 = 30.0
    assert float(event_data["target_amount"]) == 30.0
    assert float(event_data["collected_amount"]) == 0.0

    # 7. Check contributions in DB
    event_id = uuid.UUID(event_data["id"])
    stmt = select(WelfareContribution).where(WelfareContribution.event_id == event_id)
    contributions = (await db_session.execute(stmt)).scalars().all()
    assert len(contributions) == 3
    for c in contributions:
        assert float(c.amount) == 10.00
        assert c.status == ContributionStatus.PENDING

    # 8. Active member checks their obligations
    member_res = await client.get(
        "/api/v1/welfare-events/my-obligations",
        headers={"Authorization": f"Bearer {active_tokens[0]}"},
    )
    assert member_res.status_code == 200
    obligations = member_res.json()["data"]
    assert len(obligations) == 1
    assert obligations[0]["amount"] == 10.0
    assert obligations[0]["deceased_member_name"] == "Late Member Ramesh"

    # 9. Test recording payment reconciliation
    contrib_id = uuid.UUID(obligations[0]["contribution_id"])
    updated_contrib = await WelfareService.record_contribution_payment(
        db=db_session,
        contribution_id=contrib_id,
        payment_method="UPI_RAZORPAY",
    )
    assert updated_contrib.status == ContributionStatus.SUCCESS
    assert updated_contrib.payment_method == "UPI_RAZORPAY"

    # Verify event's collected amount incremented by 10.0
    updated_event = await WelfareService.get_event_by_id(db_session, event_id)
    assert float(updated_event.collected_amount) == 10.0
