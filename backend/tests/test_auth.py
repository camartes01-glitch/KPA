"""
Tests for Authentication & RBAC flows.
- OTP request & verification
- JWT issuance & token rotation
- Session management & logout
- Protected endpoint authorization & RBAC scoping
"""
import pytest
from app.core.security import create_access_token
from app.models.user import User, UserRole, UserStatus


@pytest.mark.asyncio
async def test_send_otp_success(client):
    """POST /api/v1/auth/otp/send with valid Indian phone number."""
    response = await client.post(
        "/api/v1/auth/otp/send",
        json={"phone": "9876543210"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["phone"] == "+919876543210"
    assert "dev_code" in data["data"]


@pytest.mark.asyncio
async def test_send_otp_invalid_phone(client):
    """POST /api/v1/auth/otp/send with invalid phone should fail validation."""
    response = await client.post(
        "/api/v1/auth/otp/send",
        json={"phone": "12345"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_verify_otp_success(client):
    """Verify OTP flow: send OTP -> verify OTP -> get JWT tokens."""
    # 1. Send OTP
    send_res = await client.post(
        "/api/v1/auth/otp/send",
        json={"phone": "9988776655"},
    )
    assert send_res.status_code == 200
    otp_code = send_res.json()["data"]["dev_code"]

    # 2. Verify OTP
    verify_res = await client.post(
        "/api/v1/auth/otp/verify",
        json={
            "phone": "9988776655",
            "otp": otp_code,
            "device_name": "Test Device Chrome",
        },
    )
    assert verify_res.status_code == 200
    token_data = verify_res.json()["data"]
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert token_data["user"]["phone"] == "+919988776655"
    assert token_data["user"]["role"] == "MEMBER"


@pytest.mark.asyncio
async def test_verify_otp_invalid_code(client):
    """Verify OTP with wrong code should return 400."""
    await client.post(
        "/api/v1/auth/otp/send",
        json={"phone": "9123456780"},
    )
    verify_res = await client.post(
        "/api/v1/auth/otp/verify",
        json={
            "phone": "9123456780",
            "otp": "000000",
        },
    )
    assert verify_res.status_code == 400
    assert "Invalid OTP" in verify_res.json()["detail"]


@pytest.mark.asyncio
async def test_token_refresh_rotation(client):
    """Test refresh token rotation."""
    send_res = await client.post("/api/v1/auth/otp/send", json={"phone": "9811223344"})
    otp_code = send_res.json()["data"]["dev_code"]

    login_res = await client.post(
        "/api/v1/auth/otp/verify",
        json={"phone": "9811223344", "otp": otp_code},
    )
    initial_tokens = login_res.json()["data"]
    old_refresh = initial_tokens["refresh_token"]

    # Refresh
    refresh_res = await client.post(
        "/api/v1/auth/token/refresh",
        json={"refresh_token": old_refresh},
    )
    assert refresh_res.status_code == 200
    new_tokens = refresh_res.json()["data"]
    assert new_tokens["access_token"] != initial_tokens["access_token"]
    assert new_tokens["refresh_token"] != old_refresh

    # Old refresh token must now be revoked
    stale_res = await client.post(
        "/api/v1/auth/token/refresh",
        json={"refresh_token": old_refresh},
    )
    assert stale_res.status_code == 401


@pytest.mark.asyncio
async def test_get_me_profile(client):
    """GET /api/v1/auth/me with Bearer token."""
    send_res = await client.post("/api/v1/auth/otp/send", json={"phone": "9845012345"})
    otp = send_res.json()["data"]["dev_code"]

    login_res = await client.post(
        "/api/v1/auth/otp/verify",
        json={"phone": "9845012345", "otp": otp},
    )
    access_token = login_res.json()["data"]["access_token"]

    # Unauthenticated should fail
    unauth_res = await client.get("/api/v1/auth/me")
    assert unauth_res.status_code == 403 or unauth_res.status_code == 401

    # Authenticated
    me_res = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert me_res.status_code == 200
    assert me_res.json()["data"]["phone"] == "+919845012345"


@pytest.mark.asyncio
async def test_logout(client):
    """POST /api/v1/auth/logout revokes session."""
    send_res = await client.post("/api/v1/auth/otp/send", json={"phone": "9870001122"})
    otp = send_res.json()["data"]["dev_code"]

    login_res = await client.post(
        "/api/v1/auth/otp/verify",
        json={"phone": "9870001122", "otp": otp},
    )
    tokens = login_res.json()["data"]

    logout_res = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert logout_res.status_code == 200

    # Refresh after logout should fail
    refresh_res = await client.post(
        "/api/v1/auth/token/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh_res.status_code == 401
