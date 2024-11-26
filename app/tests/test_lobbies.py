import pytest
from app.models.lobby import Lobby
from app.models.player import Player

def test_create_lobby(client, mock_udp_manager):
    """Test lobby creation"""
    response = client.post(
        "/lobbies/create",
        params={"lobby_name": "test_lobby"}  # Using 'params' to match API expectations
    )
    
    assert response.status_code == 200
    assert response.json() == {"message": "Lobby 'test_lobby' created"}
    
    # Verify UDPManager interaction
    mock_udp_manager.create_server.assert_called_once_with(
        lobby_id="test_lobby",
        host="127.0.0.1", 
        port=12345
    )

def test_join_lobby(client, mock_udp_manager):
    """Test joining a lobby"""
    # First, create a lobby
    client.post("/lobbies/create", params={"lobby_name": "test_lobby"})
    
    # Then join the lobby
    response = client.post(
        "/lobbies/join",
        params={
            "lobby_name": "test_lobby",
            "player_id": "player1"
        }
    )
    
    assert response.status_code == 200
    assert response.json() == {"message": "Player 'player1' joined lobby 'test_lobby'"}
    
    # Verify UDPManager interaction
    mock_udp_manager.create_client.assert_called_once_with(
        client_id="player1",
        server_host="127.0.0.1",
        server_port=12345
    )

def test_list_lobbies(client):
    """Test listing all lobbies"""
    # Create a test lobby
    client.post("/lobbies/create", params={"lobby_name": "test_lobby"})
    
    response = client.get("/lobbies/list")
    assert response.status_code == 200
    
    lobbies = response.json()
    assert isinstance(lobbies, list)
    assert len(lobbies) > 0
    assert any(lobby["name"] == "test_lobby" for lobby in lobbies)
