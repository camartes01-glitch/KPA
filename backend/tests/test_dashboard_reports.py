"""
Tests for Dashboards and Reports — KPI Aggregations and CSV Data Exports.
"""
from datetime import date
import pytest
from app.core.security import create_access_token
from app.models.member import Member, MemberStatus
from app.models.payment import Payment, PaymentStatus
from app.models.user import User, UserRole, UserStatus
from app.models.welfare import WelfareEvent, WelfareEventStatus
from app.services.geo_service import GeoService


@pytest.mark.asyncio
async def test_dashboard_metrics_aggregation(client, db_session):
    """Test dashboard metrics for STATE_HEAD."""
    await GeoService.seed_karnataka_data(db_session)
    dist = (await GeoService.get_all_districts(db_session))[0]
    taluka = (await GeoService.get_talukas_by_district(db_session, dist.id))[0]

    admin = User(
        phone="+919876577001",
        name="State Leader",
        role=UserRole.STATE_HEAD,
        status=UserStatus.ACTIVE,
        is_active=True,
    )
    user = User(
        phone="+919876577002",
        name="Member One",
        role=UserRole.MEMBER,
        status=UserStatus.ACTIVE,
        is_active=True,
    )
    db_session.add_all([admin, user])
    await db_session.flush()

    member = Member(
        user_id=user.id,
        membership_no="KPA-BLRU-00999",
        full_name="Member One",
        gender="MALE",
        dob=date(1990, 1, 1),
        district_id=dist.id,
        taluka_id=taluka.id,
        status=MemberStatus.APPROVED,
    )
    db_session.add(member)
    await db_session.flush()

    event = WelfareEvent(
        deceased_member_id=member.id,
        title="Dashboard Test Welfare Event",
        death_date=date(2026, 8, 1),
        target_amount=100.0,
        collected_amount=50.0,
        status=WelfareEventStatus.ACTIVE,
        created_by_id=admin.id,
    )
    payment = Payment(
        member_id=member.id,
        gateway_order_id="order_dash_test_1",
        amount=50.0,
        currency="INR",
        status=PaymentStatus.CAPTURED,
        receipt_no="RCP-DASH-001",
    )
    db_session.add_all([event, payment])
    await db_session.commit()

    token = create_access_token(subject=str(admin.id), role=admin.role.value)

    res = await client.get(
        "/api/v1/dashboard/metrics",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    metrics = res.json()["data"]
    assert metrics["total_members"] == 1
    assert metrics["active_members"] == 1
    assert metrics["active_welfare_events"] == 1
    assert metrics["total_collected_today"] == 50.0
    assert metrics["district_breakdown"] is not None


@pytest.mark.asyncio
async def test_csv_exports(client, db_session):
    """Test CSV export generation for members and financials."""
    await GeoService.seed_karnataka_data(db_session)
    dist = (await GeoService.get_all_districts(db_session))[0]
    taluka = (await GeoService.get_talukas_by_district(db_session, dist.id))[0]

    admin = User(
        phone="+919876577099",
        name="Auditor General",
        role=UserRole.STATE_HEAD,
        status=UserStatus.ACTIVE,
        is_active=True,
    )
    user = User(
        phone="+919876577088",
        name="Photographer Ramesh",
        role=UserRole.MEMBER,
        status=UserStatus.ACTIVE,
        is_active=True,
    )
    db_session.add_all([admin, user])
    await db_session.flush()

    member = Member(
        user_id=user.id,
        membership_no="KPA-BLRU-00888",
        full_name="Photographer Ramesh",
        gender="MALE",
        dob=date(1989, 5, 20),
        studio_name="Star Studio",
        district_id=dist.id,
        taluka_id=taluka.id,
        status=MemberStatus.APPROVED,
    )
    db_session.add(member)
    await db_session.commit()

    token = create_access_token(subject=str(admin.id), role=admin.role.value)

    # 1. Export members CSV
    res_mem = await client.get(
        "/api/v1/reports/members/csv",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_mem.status_code == 200
    assert "text/csv" in res_mem.headers["content-type"]
    csv_text = res_mem.text
    assert "Membership No,Full Name,Gender" in csv_text
    assert "Photographer Ramesh" in csv_text
    assert "Star Studio" in csv_text

    # 2. Export financial audit CSV
    res_fin = await client.get(
        "/api/v1/reports/financial/csv",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_fin.status_code == 200
    assert "Receipt No,Member Name,Membership No" in res_fin.text
