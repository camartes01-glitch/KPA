"""
Tests for Geographic Data — Districts and Talukas across Karnataka.
"""
import pytest
from app.core.security import create_access_token
from app.models.user import User, UserRole, UserStatus


@pytest.mark.asyncio
async def test_seed_and_list_districts(client):
    """Seed Karnataka data and verify all 31 districts are returned."""
    # 1. Seed
    seed_res = await client.post("/api/v1/geo/seed")
    assert seed_res.status_code == 200
    assert seed_res.json()["data"]["districts_seeded"] == 31

    # 2. List districts
    list_res = await client.get("/api/v1/geo/districts")
    assert list_res.status_code == 200
    districts = list_res.json()["data"]
    assert len(districts) == 31

    # Check bilingual properties on Bengaluru Urban
    blr_urban = next((d for d in districts if d["code"] == "BLR_U"), None)
    assert blr_urban is not None
    assert blr_urban["name_en"] == "Bengaluru Urban"
    assert "ಬೆಂಗಳೂರು" in blr_urban["name_kn"]


@pytest.mark.asyncio
async def test_get_district_with_talukas(client):
    """Retrieve single district with its associated talukas."""
    await client.post("/api/v1/geo/seed")
    list_res = await client.get("/api/v1/geo/districts")
    blr_urban = next(d for d in list_res.json()["data"] if d["code"] == "BLR_U")

    # Fetch district by ID
    get_res = await client.get(f"/api/v1/geo/districts/{blr_urban['id']}")
    assert get_res.status_code == 200
    data = get_res.json()["data"]
    assert data["name_en"] == "Bengaluru Urban"
    assert len(data["talukas"]) >= 5
    taluka_names = [t["name_en"] for t in data["talukas"]]
    assert "Bengaluru North" in taluka_names
    assert "Anekal" in taluka_names


@pytest.mark.asyncio
async def test_get_talukas_by_district(client):
    """List talukas for a specific district."""
    await client.post("/api/v1/geo/seed")
    list_res = await client.get("/api/v1/geo/districts")
    mysuru = next(d for d in list_res.json()["data"] if d["code"] == "MYS")

    taluka_res = await client.get(f"/api/v1/geo/districts/{mysuru['id']}/talukas")
    assert taluka_res.status_code == 200
    talukas = taluka_res.json()["data"]
    assert len(talukas) >= 5
    names = [t["name_en"] for t in talukas]
    assert "Hunsur" in names
    assert "Nanjangud" in names


@pytest.mark.asyncio
async def test_district_create_rbac(client, db_session):
    """Only STATE_HEAD can manually create districts."""
    # Create STATE_HEAD user
    state_head = User(
        phone="+919900000001",
        name="State Leader",
        role=UserRole.STATE_HEAD,
        status=UserStatus.ACTIVE,
        is_active=True,
    )
    db_session.add(state_head)

    # Create normal member
    member = User(
        phone="+919900000002",
        name="Photographer Member",
        role=UserRole.MEMBER,
        status=UserStatus.ACTIVE,
        is_active=True,
    )
    db_session.add(member)
    await db_session.commit()

    member_token = create_access_token(subject=str(member.id), role=member.role.value)
    state_token = create_access_token(subject=str(state_head.id), role=state_head.role.value)

    # Member attempt should be 403 Forbidden
    forbidden_res = await client.post(
        "/api/v1/geo/districts",
        headers={"Authorization": f"Bearer {member_token}"},
        json={"name_en": "Test District", "name_kn": "ಟೆಸ್ಟ್ ಜಿಲ್ಲೆ", "code": "TST"},
    )
    assert forbidden_res.status_code == 403

    # State Head attempt should succeed
    success_res = await client.post(
        "/api/v1/geo/districts",
        headers={"Authorization": f"Bearer {state_token}"},
        json={"name_en": "Custom Region", "name_kn": "ಕಸ್ಟಮ್ ಪ್ರಾಂತ್ಯ", "code": "CST"},
    )
    assert success_res.status_code == 200
    assert success_res.json()["data"]["code"] == "CST"
