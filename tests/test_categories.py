"""Tests for categories endpoints."""
import pytest
import uuid
from unittest.mock import patch, MagicMock

pytestmark = pytest.mark.asyncio


def _make_mock_client(return_data=None):
    """Helper to build a Supabase mock client."""
    if return_data is None:
        return_data = {}
    mock = MagicMock()
    result = MagicMock()
    result.data = [return_data] if return_data else []
    result.count = len(result.data)
    # chain: .table().select().order().execute()
    mock.table.return_value.select.return_value.order.return_value.execute.return_value = result
    mock.table.return_value.insert.return_value.execute.return_value = result
    mock.table.return_value.update.return_value.eq.return_value.execute.return_value = result
    mock.table.return_value.delete.return_value.eq.return_value.execute.return_value = result
    mock.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(data=[])
    return mock


async def test_list_categories(client):
    """GET /api/categories should return list."""
    fake_category = {
        "id": str(uuid.uuid4()),
        "name": "Alimentación",
        "description": "Gastos en comida",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }
    mock_client = _make_mock_client(fake_category)
    with patch("app.routes.categories.get_supabase_client", return_value=mock_client):
        response = await client.get("/api/categories")
    assert response.status_code == 200
    data = await response.get_json()
    assert data["success"] is True
    assert isinstance(data["data"], list)


async def test_create_category(client):
    """POST /api/categories should create and return category."""
    cat_id = str(uuid.uuid4())
    fake_category = {
        "id": cat_id,
        "name": "Transporte",
        "description": "Gastos de transporte",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }
    mock_client = _make_mock_client(fake_category)
    with patch("app.routes.categories.get_supabase_client", return_value=mock_client):
        response = await client.post(
            "/api/categories",
            json={"name": "Transporte", "description": "Gastos de transporte"},
        )
    assert response.status_code == 201
    data = await response.get_json()
    assert data["success"] is True
    assert data["data"]["name"] == "Transporte"


async def test_create_category_missing_name(client):
    """POST /api/categories without name should fail with 422."""
    response = await client.post("/api/categories", json={"description": "No name"})
    assert response.status_code == 422
    data = await response.get_json()
    assert data["success"] is False


async def test_create_category_empty_name(client):
    """POST /api/categories with empty name should fail with 422."""
    response = await client.post("/api/categories", json={"name": ""})
    assert response.status_code == 422
    data = await response.get_json()
    assert data["success"] is False
