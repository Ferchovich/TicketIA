"""Pytest configuration and fixtures for TicketIA tests."""
import pytest
import pytest_asyncio
from unittest.mock import MagicMock, AsyncMock, patch

from app import create_app


@pytest.fixture
def app():
    """Create a test application instance."""
    application = create_app()
    application.config["TESTING"] = True
    return application


@pytest_asyncio.fixture
async def client(app):
    """Create a test client."""
    async with app.test_client() as client:
        yield client


@pytest.fixture
def mock_supabase():
    """Mock Supabase client."""
    mock = MagicMock()
    # Chain: .table().select().execute() → returns result with .data
    mock_result = MagicMock()
    mock_result.data = []
    mock_result.count = 0
    mock.table.return_value.select.return_value.execute.return_value = mock_result
    mock.table.return_value.insert.return_value.execute.return_value = mock_result
    return mock
