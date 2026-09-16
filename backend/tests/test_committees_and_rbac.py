"""
Tests for Committees, Administrator Management, and Rate Limiting Middleware.
"""
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.user import User, UserRole, UserStatus
from app.services.geo_service import GeoService


@pytest.mark.asyncio
async def test_committees_roster_and_appointments(client: AsyncClient, db_session: AsyncSession):
    """Test retrieving committees, appointing an office bearer, and removing an office bearer."""
    # 1. Setup STATE_HEAD
    state_head = User(
        phone="+919988112233",
        name="State President",
        role=UserRole.STATE_HEAD,
        status=UserStatus.ACTIVE,
        is_active=True,
    )
    db_session.add(state_head)
    await db_session.commit()
    token = create_access_token(subject=str(state_head.id), role=state_head.role.value)

    # 2. Get initial roster
    res = await client.get("/api/v1/committees", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 3

    # 3. Appoint new office bearer
    appoint_res = await client.post(
        "/api/v1/committees",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Sri K. Raghavendra",
            "phone": "+919888877777",
            "email": "raghu@kpa.org.in",
            "designation": "Vice President",
            "committee_level": "STATE",
            "tenure_start": "2024-06-01",
            "tenure_end": "2026-06-01",
        },
    )
    assert appoint_res.status_code == 200
    created = appoint_res.json()["data"]
    assert created["name"] == "Sri K. Raghavendra"
    assert created["designation"] == "Vice President"
    created_id = created["id"]

    # 4. Remove office bearer
    del_res = await client.delete(
        f"/api/v1/committees/{created_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert del_res.status_code == 200
    assert del_res.json()["data"]["id"] == created_id


@pytest.mark.asyncio
async def test_admin_creation_and_status_update(client: AsyncClient, db_session: AsyncSession):
    """Test creating a District Administrator and updating status."""
    await GeoService.seed_karnataka_data(db_session)
    districts = await GeoService.get_all_districts(db_session)
    target_dist = districts[0]

    state_head = User(
        phone="+919988001122",
        name="State Leader",
        role=UserRole.STATE_HEAD,
        status=UserStatus.ACTIVE,
        is_active=True,
    )
    db_session.add(state_head)
    await db_session.commit()
    token = create_access_token(subject=str(state_head.id), role=state_head.role.value)

    # 1. Create District Admin
    create_res = await client.post(
        "/api/v1/auth/admins",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "phone": "+919977665544",
            "name": "Ravi Gowda",
            "email": "ravi@kpa.org.in",
            "role": "DISTRICT_ADMIN",
            "district_id": str(target_dist.id),
        },
    )
    assert create_res.status_code == 200
    admin_data = create_res.json()["data"]
    assert admin_data["role"] == "DISTRICT_ADMIN"
    assert admin_data["name"] == "Ravi Gowda"
    admin_id = admin_data["id"]

    # 2. Update status / deactivation
    patch_res = await client.patch(
        f"/api/v1/auth/admins/{admin_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"is_active": False},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["data"]["is_active"] is False


@pytest.mark.asyncio
async def test_rate_limit_headers_present(client: AsyncClient):
    """Verify rate limit headers are present on API responses."""
    res = await client.get("/api/v1/health")
    assert res.status_code == 200

    # API endpoints under /api/v1/geo should contain X-RateLimit-Limit
    res_geo = await client.get("/api/v1/geo/districts")
    assert res_geo.status_code == 200
    assert "X-RateLimit-Limit" in res_geo.headers
    assert "X-RateLimit-Remaining" in res_geo.headers
