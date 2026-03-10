"""Tests for health endpoint."""
import pytest

pytestmark = pytest.mark.asyncio


async def test_health_check(client):
    """Health endpoint should return 200 with success=True."""
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = await response.get_json()
    assert data["success"] is True
    assert data["data"]["status"] == "ok"


async def test_health_message(client):
    """Health endpoint should include a message."""
    response = await client.get("/api/health")
    data = await response.get_json()
    assert "message" in data
    assert data["message"] != ""
