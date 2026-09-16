"""
Tests for Google OAuth2 Authentication flow.
- Token verification failure handling (401)
- New user registration via Google ID Token
- Existing user login and google_sub linking
- Non-gmail domain rejection (403)
- Suspended / Inactive account rejection (403)
"""
from unittest.mock import patch
import pytest

from app.models.user import User, UserRole, UserStatus


@pytest.mark.asyncio
async def test_google_auth_invalid_token(client):
    """POST /api/v1/auth/google with invalid ID token should return 401."""
    response = await client.post(
        "/api/v1/auth/google",
        json={"id_token": "fake-invalid-token"},
    )
    assert response.status_code == 401
    assert "Invalid Google ID token" in response.json()["detail"]


@pytest.mark.asyncio
async def test_google_auth_success_new_user(client):
    """POST /api/v1/auth/google creates new user and returns JWT tokens."""
    mock_payload = {
        "sub": "google-user-12345",
        "email": "photographer1@gmail.com",
        "email_verified": True,
        "name": "Ravi Kumar",
        "picture": "https://lh3.googleusercontent.com/a/photo.jpg",
    }

    with patch("app.services.google_auth_service.GoogleAuthService.verify_google_id_token", return_value=mock_payload):
        response = await client.post(
            "/api/v1/auth/google",
            json={"id_token": "valid-mocked-token", "device_name": "Chrome on Windows"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        token_data = data["data"]
        assert "access_token" in token_data
        assert "refresh_token" in token_data
        assert token_data["token_type"] == "bearer"
        assert token_data["user"]["email"] == "photographer1@gmail.com"
        assert token_data["user"]["name"] == "Ravi Kumar"
        assert token_data["user"]["role"] == "MEMBER"


@pytest.mark.asyncio
async def test_google_auth_links_existing_user(client, db_session):
    """POST /api/v1/auth/google links google_sub to existing user by email."""
    # Pre-create user with same email but no google_sub
    existing_user = User(
        email="district.head@gmail.com",
        phone="+919876500001",
        name="District Admin User",
        role=UserRole.DISTRICT_ADMIN,
        status=UserStatus.ACTIVE,
        is_active=True,
    )
    db_session.add(existing_user)
    await db_session.commit()

    mock_payload = {
        "sub": "google-sub-9999",
        "email": "district.head@gmail.com",
        "email_verified": True,
        "name": "District Admin User",
        "picture": None,
    }

    with patch("app.services.google_auth_service.GoogleAuthService.verify_google_id_token", return_value=mock_payload):
        response = await client.post(
            "/api/v1/auth/google",
            json={"id_token": "valid-mocked-token"},
        )
        assert response.status_code == 200
        token_data = response.json()["data"]
        assert token_data["user"]["email"] == "district.head@gmail.com"
        assert token_data["user"]["role"] == "DISTRICT_ADMIN"


@pytest.mark.asyncio
async def test_google_auth_rejects_non_gmail(client):
    """POST /api/v1/auth/google rejects non-gmail email addresses."""
    mock_payload = {
        "sub": "google-workspace-user",
        "email": "admin@external-company.org",
        "email_verified": True,
        "name": "External User",
        "picture": None,
    }

    with patch("app.services.google_auth_service.GoogleAuthService.verify_google_id_token", return_value=mock_payload):
        response = await client.post(
            "/api/v1/auth/google",
            json={"id_token": "valid-mocked-token"},
        )
        assert response.status_code == 403
        assert "@gmail.com" in response.json()["detail"]


@pytest.mark.asyncio
async def test_google_auth_rejects_suspended_user(client, db_session):
    """POST /api/v1/auth/google rejects suspended user accounts."""
    suspended_user = User(
        email="suspended.photographer@gmail.com",
        name="Suspended User",
        role=UserRole.MEMBER,
        status=UserStatus.SUSPENDED,
        is_active=True,
    )
    db_session.add(suspended_user)
    await db_session.commit()

    mock_payload = {
        "sub": "google-sub-suspended",
        "email": "suspended.photographer@gmail.com",
        "email_verified": True,
        "name": "Suspended User",
        "picture": None,
    }

    with patch("app.services.google_auth_service.GoogleAuthService.verify_google_id_token", return_value=mock_payload):
        response = await client.post(
            "/api/v1/auth/google",
            json={"id_token": "valid-mocked-token"},
        )
        assert response.status_code == 403
        assert "suspended" in response.json()["detail"].lower()


def test_clock_skew_tolerates_near_future_iat():
    """Verify that a token issued 1-2 seconds ahead (legitimate clock skew) is accepted."""
    import time
    from google.auth import jwt

    now = int(time.time())
    # iat is 2 seconds in future (like 1789532475 < 1789532476)
    payload = {
        "iat": now + 2,
        "exp": now + 3600,
        "sub": "user-clock-skew",
        "email": "skew.user@gmail.com",
    }
    # With 300s skew tolerance, this must not raise any exception
    jwt._verify_iat_and_exp(payload, clock_skew_in_seconds=300)


def test_clock_skew_rejects_truly_expired_token():
    """Verify that a token expired well beyond the clock skew tolerance (e.g. 10m ago) is rejected."""
    import time
    from google.auth import jwt, exceptions

    now = int(time.time())
    payload = {
        "iat": now - 7200,
        "exp": now - 600,  # expired 10 minutes ago (> 300s tolerance)
        "sub": "expired-user",
        "email": "expired@gmail.com",
    }
    with pytest.raises(exceptions.InvalidValue, match="Token expired"):
        jwt._verify_iat_and_exp(payload, clock_skew_in_seconds=300)


def test_clock_skew_rejects_far_future_token():
    """Verify that a token with iat far in the future (> 300s tolerance) is rejected."""
    import time
    from google.auth import jwt, exceptions

    now = int(time.time())
    payload = {
        "iat": now + 600,  # 10 minutes in future (> 300s tolerance)
        "exp": now + 4200,
        "sub": "future-user",
        "email": "future@gmail.com",
    }
    with pytest.raises(exceptions.InvalidValue, match="Token used too early"):
        jwt._verify_iat_and_exp(payload, clock_skew_in_seconds=300)


def test_verify_google_id_token_passes_clock_skew():
    """Verify that GoogleAuthService.verify_google_id_token passes clock_skew_in_seconds=300."""
    from app.services.google_auth_service import GoogleAuthService

    mock_verified_payload = {
        "iss": "https://accounts.google.com",
        "sub": "clock-skew-sub-123",
        "email": "test.skew@gmail.com",
        "email_verified": True,
        "name": "Skew Test",
        "picture": None,
    }

    with patch(
        "google.oauth2.id_token.verify_oauth2_token",
        return_value=mock_verified_payload,
    ) as mock_verify:
        res = GoogleAuthService.verify_google_id_token("mock-token")
        assert res["email"] == "test.skew@gmail.com"
        assert res["sub"] == "clock-skew-sub-123"

        # Check call arguments
        mock_verify.assert_called_once()
        _, kwargs = mock_verify.call_args
        assert kwargs.get("clock_skew_in_seconds") == 300

