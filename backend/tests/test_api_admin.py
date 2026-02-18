import pytest


@pytest.mark.asyncio
async def test_admin_status(client):
    response = await client.get("/api/admin/status")
    assert response.status_code == 200
    data = response.json()
    assert "scheduler_running" in data
    assert "total_surge_events" in data
    assert "total_tickers" in data


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
