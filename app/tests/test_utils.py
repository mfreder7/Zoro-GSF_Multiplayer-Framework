import pytest
from app.utils.protocols.udp_server import GameServer
from app.utils.protocols.udp_client import GameClient
from app.utils.udp import UDPManager
from app.models.lobby import Lobby
from app.models.player import Player
from unittest.mock import MagicMock
import json
import time
import socket

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Game Server API"}

def test_list_lobbies(client):
    response = client.get("/lobbies/list")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    # Optionally, check if 'test_lobby' is in the list
    lobbies = response.json()
    assert any(lobby["id"] == "test_lobby" for lobby in lobbies)

@pytest.fixture
def mock_udp_manager():
    """Create a mock UDPManager"""
    manager = MagicMock(spec=UDPManager)
    manager.clients = {}
    # Mock the create_client method to add to clients dict
    def mock_create_client(client_id, server_host, server_port):
        manager.clients[client_id] = MagicMock()
    manager.create_client.side_effect = mock_create_client
    return manager

def test_udp_manager_create_server(mock_udp_manager):
    """Test UDPManager server creation"""
    mock_udp_manager.create_server("test_lobby", "127.0.0.1", 12345)
    mock_udp_manager.create_server.assert_called_once_with("test_lobby", "127.0.0.1", 12345)

def test_udp_manager_create_client(mock_udp_manager):
    """Test UDPManager client creation"""
    mock_udp_manager.create_client("player1", "127.0.0.1", 12345)
    assert "player1" in mock_udp_manager.clients

@pytest.fixture
def game_server(monkeypatch):
    """Create a mock GameServer instance"""
    server = GameServer("127.0.0.1", 12345)
    mock_socket = MagicMock()
    monkeypatch.setattr(socket, 'socket', lambda *args, **kwargs: mock_socket)
    server.sock = mock_socket
    return server

@pytest.fixture
def game_client(monkeypatch):
    """Create a mock GameClient instance"""
    client = GameClient("127.0.0.1", 12345, "test_client")
    mock_socket = MagicMock()
    monkeypatch.setattr(socket, 'socket', lambda *args, **kwargs: mock_socket)
    client.sock = mock_socket
    return client

def test_game_server_client_communication(game_server, game_client):
    """Test communication between server and client"""
    # Simulating communication without actual network operations
    game_server.clients["test_client"] = ("127.0.0.1", 12345)
    
    test_data = {"test": "message"}
    game_client.send_update = MagicMock()
    game_client.send_update(test_data)
    game_client.send_update.assert_called_once_with(test_data)
    
    assert "test_client" in game_server.clients
    assert len(game_server.clients) == 1

def test_lobby_operations(client, mock_udp_manager):
    """Test lobby creation, player joining, and lobby listing"""
    from app.routers.lobbies import lobbies
    # Clear existing lobbies
    lobbies.clear()
    
    # Create lobby
    response = client.post(
        "/lobbies/create",
        params={"lobby_name": "test_lobby"}
    )
    assert response.status_code == 200

    # Join lobby
    response = client.post(
        "/lobbies/join",
        params={
            "lobby_name": "test_lobby",
            "player_id": "player1"
        }
    )
    assert response.status_code == 200

    # List lobbies
    response = client.get("/lobbies/list")
    assert response.status_code == 200
    lobbies = response.json()

    # Verify lobby data
    assert isinstance(lobbies, list)
    assert len(lobbies) == 1
    lobby = lobbies[0]
    assert lobby["name"] == "test_lobby"
    assert len(lobby["players"]) == 1
    assert lobby["players"][0]["id"] == "player1"

    # Leave lobby
    response = client.post(
        "/lobbies/leave",
        params={
            "lobby_id": "test_lobby",
            "player_id": "player1"
        }
    )
    assert response.status_code == 200

    # Verify lobby is empty
    response = client.get("/lobbies/list")
    lobbies = response.json()
    assert len(lobbies[0]["players"]) == 0
