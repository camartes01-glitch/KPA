"""
Tests for the health check endpoints.
"""
import pytest


@pytest.mark.asyncio
async def test_health_liveness(client):
    """GET /api/v1/health should return 200 with status ok."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "uptime_seconds" in data


@pytest.mark.asyncio
async def test_root_health(client):
    """GET /health (root) should return 200."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
