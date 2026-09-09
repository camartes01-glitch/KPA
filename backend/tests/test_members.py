"""
Tests for Member Management — Registration, Approval, Sequential ID Generation, and Digital Cards with QR.
"""
from datetime import date
import pytest
from app.core.security import create_access_token
from app.models.user import User, UserRole, UserStatus
from app.services.geo_service import GeoService


@pytest.mark.asyncio
async def test_member_registration(client, db_session):
    """Test full photographer registration flow."""
    # 1. Seed geo
    await GeoService.seed_karnataka_data(db_session)
    districts = await GeoService.get_all_districts(db_session)
    blr_u = next(d for d in districts if d.code == "BLR_U")
    talukas = await GeoService.get_talukas_by_district(db_session, blr_u.id)
    taluka = talukas[0]

    # 2. Authenticate user
    user = User(
        phone="+919876500001",
        name="Ramesh Photographer",
        role=UserRole.MEMBER,
        status=UserStatus.PENDING,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    token = create_access_token(subject=str(user.id), role=user.role.value)

    # 3. Submit registration
    reg_payload = {
        "full_name": "Ramesh Kumar",
        "father_or_spouse_name": "Suresh Kumar",
        "gender": "MALE",
        "dob": "1990-05-15",
        "blood_group": "O+",
        "studio_name": "Ramesh Digital Studio",
        "experience_years": 12,
        "address_line": "123 MG Road",
        "pincode": "560001",
        "district_id": str(blr_u.id),
        "taluka_id": str(taluka.id),
        "nominee": {
            "name": "Sunita Kumar",
            "relationship_to_member": "Spouse",
            "phone": "+919876500002",
            "aadhaar_last_4": "1234",
            "bank_account_no": "123456789012",
            "bank_ifsc": "SBIN0001234",
            "bank_name": "State Bank of India",
        },
    }

    res = await client.post(
        "/api/v1/members/register",
        headers={"Authorization": f"Bearer {token}"},
        json=reg_payload,
    )
    assert res.status_code == 200
    member_data = res.json()["data"]
    assert member_data["full_name"] == "Ramesh Kumar"
    assert member_data["status"] == "PENDING"
    assert member_data["membership_no"] is None


@pytest.mark.asyncio
async def test_member_approval_and_id_generation(client, db_session):
    """Test approval generates unique sequential membership ID and digital card."""
    await GeoService.seed_karnataka_data(db_session)
    districts = await GeoService.get_all_districts(db_session)
    blr_u = next(d for d in districts if d.code == "BLR_U")
    talukas = await GeoService.get_talukas_by_district(db_session, blr_u.id)

    # Register member
    member_user = User(
        phone="+919876500010",
        name="Anand Photo",
        role=UserRole.MEMBER,
        status=UserStatus.PENDING,
        is_active=True,
    )
    # Admin user
    admin_user = User(
        phone="+919876500099",
        name="State Admin",
        role=UserRole.STATE_HEAD,
        status=UserStatus.ACTIVE,
        is_active=True,
    )
    db_session.add_all([member_user, admin_user])
    await db_session.commit()

    member_token = create_access_token(subject=str(member_user.id), role=member_user.role.value)
    admin_token = create_access_token(subject=str(admin_user.id), role=admin_user.role.value)

    # Register
    reg_res = await client.post(
        "/api/v1/members/register",
        headers={"Authorization": f"Bearer {member_token}"},
        json={
            "full_name": "Anand Rao",
            "gender": "MALE",
            "dob": "1988-08-20",
            "district_id": str(blr_u.id),
            "taluka_id": str(talukas[0].id),
            "nominee": {
                "name": "Geetha Rao",
                "relationship_to_member": "Spouse",
                "phone": "+919876500011",
            },
        },
    )
    member_id = reg_res.json()["data"]["id"]

    # Approve application
    approve_res = await client.post(
        f"/api/v1/members/{member_id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert approve_res.status_code == 200
    approved_data = approve_res.json()["data"]
    assert approved_data["status"] == "APPROVED"
    assert approved_data["membership_no"] == "KPA-BLRU-00001"

    # Get digital card with QR
    card_res = await client.get(
        "/api/v1/members/me/card",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert card_res.status_code == 200
    card_data = card_res.json()["data"]
    assert card_data["membership_no"] == "KPA-BLRU-00001"
    assert card_data["member_name"] == "Anand Rao"
    assert card_data["qr_code_base64"].startswith("data:image/png;base64,")


@pytest.mark.asyncio
async def test_member_rejection(client, db_session):
    """Test rejection workflow with reason."""
    await GeoService.seed_karnataka_data(db_session)
    districts = await GeoService.get_all_districts(db_session)
    dist = districts[0]
    talukas = await GeoService.get_talukas_by_district(db_session, dist.id)

    member_user = User(
        phone="+919876500020",
        name="Rejected Applicant",
        role=UserRole.MEMBER,
        status=UserStatus.PENDING,
        is_active=True,
    )
    admin_user = User(
        phone="+919876500021",
        name="Approver",
        role=UserRole.STATE_HEAD,
        status=UserStatus.ACTIVE,
        is_active=True,
    )
    db_session.add_all([member_user, admin_user])
    await db_session.commit()

    m_token = create_access_token(subject=str(member_user.id), role=member_user.role.value)
    a_token = create_access_token(subject=str(admin_user.id), role=admin_user.role.value)

    reg_res = await client.post(
        "/api/v1/members/register",
        headers={"Authorization": f"Bearer {m_token}"},
        json={
            "full_name": "Test Person",
            "gender": "MALE",
            "dob": "1995-01-01",
            "district_id": str(dist.id),
            "taluka_id": str(talukas[0].id),
            "nominee": {"name": "Nominee", "relationship_to_member": "Mother", "phone": "+919876500022"},
        },
    )
    m_id = reg_res.json()["data"]["id"]

    rej_res = await client.post(
        f"/api/v1/members/{m_id}/reject",
        headers={"Authorization": f"Bearer {a_token}"},
        json={"reason": "Incomplete KYC documents submitted"},
    )
    assert rej_res.status_code == 200
    rej_data = rej_res.json()["data"]
    assert rej_data["status"] == "REJECTED"
    assert rej_data["rejection_reason"] == "Incomplete KYC documents submitted"
