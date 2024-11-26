import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_udp_manager
from app.utils.udp import UDPManager
from unittest.mock import MagicMock
import socket
import threading

# Remove autouse=True to prevent unexpected side effects
@pytest.fixture
def mock_socket(monkeypatch):
    """Mock socket operations to prevent actual network usage during tests"""
    mock_socket = MagicMock()
    monkeypatch.setattr(socket, "socket", lambda *args, **kwargs: mock_socket)
    return mock_socket

@pytest.fixture
def mock_threading(monkeypatch):
    """Mock threading when needed in specific tests"""
    original_thread = threading.Thread

    class MockThread:
        def __init__(self, *args, **kwargs):
            pass

        def start(self):
            pass

        def join(self):
            pass

    monkeypatch.setattr(threading, "Thread", MockThread)
    yield
    monkeypatch.setattr(threading, "Thread", original_thread)

@pytest.fixture
def mock_udp_manager():
    """Create a UDPManager with mocked methods"""
    manager = UDPManager()

    # Mock the methods explicitly
    manager.create_server = MagicMock()
    manager.create_client = MagicMock()
    manager.remove_server = MagicMock()
    manager.remove_client = MagicMock()

    return manager

@pytest.fixture
def client(mock_udp_manager):
    """Create a test client with dependency overrides"""
    # Set the dependency override
    app.dependency_overrides[get_udp_manager] = lambda: mock_udp_manager

    # Create the TestClient instance
    with TestClient(app) as client:
        yield client

    # Clear the dependency overrides after the client is done
    app.dependency_overrides.clear()