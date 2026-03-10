"""Tests for tickets endpoints."""
import io
import struct
import uuid
import zlib
import pytest
from unittest.mock import patch, MagicMock
from werkzeug.datastructures import FileStorage

pytestmark = pytest.mark.asyncio


async def test_analyze_ticket_no_file(client):
    """POST /api/tickets/analyze without file should return 400."""
    response = await client.post("/api/tickets/analyze")
    assert response.status_code == 400
    data = await response.get_json()
    assert data["success"] is False


async def test_analyze_ticket_mock(client):
    """POST /api/tickets/analyze with a valid PNG should return extracted data."""
    # Create a minimal valid PNG (1x1 pixel white)
    def create_minimal_png():
        signature = b'\x89PNG\r\n\x1a\n'
        ihdr_data = struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)
        ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff
        ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
        raw_data = b'\x00\xff\xff\xff'
        compressed = zlib.compress(raw_data)
        idat_crc = zlib.crc32(b'IDAT' + compressed) & 0xffffffff
        idat = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc)
        iend_crc = zlib.crc32(b'IEND') & 0xffffffff
        iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)
        return signature + ihdr + idat + iend

    png_bytes = create_minimal_png()

    response = await client.post(
        "/api/tickets/analyze",
        files={
            "image": FileStorage(
                stream=io.BytesIO(png_bytes),
                filename="test.png",
                content_type="image/png",
            )
        },
    )
    assert response.status_code == 200
    data = await response.get_json()
    assert data["success"] is True
    assert "data" in data
    extracted = data["data"]
    # Mock should always return these fields
    assert "importe_total" in extracted
    assert "cuit" in extracted
    assert "confianza_extraccion" in extracted


async def test_create_ticket(client):
    """POST /api/tickets should save a ticket."""
    ticket_id = str(uuid.uuid4())
    fake_ticket = {
        "id": ticket_id,
        "document_id": None,
        "category_id": None,
        "cuit": "30712345678",
        "razon_social": "TEST SRL",
        "importe_total": 1210.0,
        "status": "pending_category",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }

    mock_client = MagicMock()
    mock_result = MagicMock()
    mock_result.data = [fake_ticket]
    mock_client.table.return_value.insert.return_value.execute.return_value = mock_result

    with patch("app.routes.tickets.get_supabase_client", return_value=mock_client):
        response = await client.post(
            "/api/tickets",
            json={
                "cuit": "30-71234567-8",
                "razon_social": "TEST SRL",
                "importe_total": 1210.0,
                "subtotal": 1000.0,
                "iva": 210.0,
                "moneda": "ARS",
            },
        )
    assert response.status_code == 201
    data = await response.get_json()
    assert data["success"] is True


async def test_list_tickets(client):
    """GET /api/tickets should return paginated list."""
    mock_client = MagicMock()
    mock_result = MagicMock()
    mock_result.data = []
    mock_result.count = 0
    # chain for find_all: .table().select().order().range().execute()
    q = mock_client.table.return_value.select.return_value
    q.gte = MagicMock(return_value=q)
    q.lte = MagicMock(return_value=q)
    q.eq = MagicMock(return_value=q)
    q.ilike = MagicMock(return_value=q)
    q.order = MagicMock(return_value=q)
    q.range = MagicMock(return_value=q)
    q.execute = MagicMock(return_value=mock_result)

    with patch("app.routes.tickets.get_supabase_client", return_value=mock_client):
        response = await client.get("/api/tickets?page=1&page_size=10")
    assert response.status_code == 200
    data = await response.get_json()
    assert data["success"] is True
    assert "pagination" in data
