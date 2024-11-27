import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_udp_manager
from app.utils.udp_manager import UDPManager
from unittest.mock import MagicMock

@pytest.fixture
def mock_udp_manager():
    """Create a mock UDPManager with only the existing methods."""
    manager = MagicMock(spec=UDPManager)
    return manager

@pytest.fixture
def client(mock_udp_manager):
    """Create a test client with dependency overrides."""
    app.dependency_overrides[get_udp_manager] = lambda: mock_udp_manager

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()