"""
Tests for Security & Audit Logs — Immutable Audit Trails, RBAC Scoping, and Security Headers.
"""
import pytest
from app.core.security import create_access_token
from app.models.user import User, UserRole, UserStatus
from app.services.audit_service import AuditService


@pytest.mark.asyncio
async def test_audit_logging_and_retrieval(client, db_session):
    """Test recording and querying immutable audit logs."""
    admin = User(
        phone="+919876566001",
        name="State Leader",
        role=UserRole.STATE_HEAD,
        status=UserStatus.ACTIVE,
        is_active=True,
    )
    member = User(
        phone="+919876566002",
        name="Member User",
        role=UserRole.MEMBER,
        status=UserStatus.ACTIVE,
        is_active=True,
    )
    db_session.add_all([admin, member])
    await db_session.commit()

    # Log an action
    await AuditService.log_action(
        db=db_session,
        action="MEMBER_APPROVED",
        resource_type="members",
        resource_id="mem-12345",
        user_id=admin.id,
        payload={"membership_no": "KPA-BLRU-00001", "approver": "State Leader"},
        ip_address="127.0.0.1",
        user_agent="Mozilla/5.0",
    )

    admin_token = create_access_token(subject=str(admin.id), role=admin.role.value)
    member_token = create_access_token(subject=str(member.id), role=member.role.value)

    # 1. Member query must be 403 Forbidden
    forbidden_res = await client.get(
        "/api/v1/audit-logs",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert forbidden_res.status_code == 403

    # 2. STATE_HEAD query must succeed
    admin_res = await client.get(
        "/api/v1/audit-logs",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert admin_res.status_code == 200
    logs = admin_res.json()["data"]
    assert len(logs) == 1
    assert logs[0]["action"] == "MEMBER_APPROVED"
    assert logs[0]["resource_type"] == "members"
    assert logs[0]["ip_address"] == "127.0.0.1"


@pytest.mark.asyncio
async def test_security_headers_present(client):
    """Test presence of security headers on responses."""
    res = await client.get("/health")
    assert res.status_code == 200
    headers = res.headers
    assert headers.get("x-content-type-options") == "nosniff"
    assert headers.get("x-frame-options") == "DENY"
    assert "x-xss-protection" in headers
