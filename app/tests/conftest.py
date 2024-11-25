import pytest
from fastapi.testclient import TestClient
from app.dependencies import get_udp_manager
from app.main import app
from app.utils.udp import UDPManager
from app.models.lobby import Lobby
from unittest.mock import MagicMock

@pytest.fixture
def mock_udp_manager():
    """Mock UDPManager with required methods"""
    manager = MagicMock(spec=UDPManager)
    # Setup default return values
    manager.create_server.return_value = None
    manager.create_client.return_value = None
    return manager

@pytest.fixture
def client(mock_udp_manager):
    """TestClient with mocked dependencies"""
    def get_mock_udp_manager():
        return mock_udp_manager
    
    app.dependency_overrides[get_udp_manager] = get_mock_udp_manager
    
    client = TestClient(app)
    yield client
    
    # Cleanup
    app.dependency_overrides.clear()