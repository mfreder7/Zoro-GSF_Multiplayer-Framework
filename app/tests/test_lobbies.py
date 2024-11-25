from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_lobby():
    response = client.post("/lobbies/create", json={"lobby_name": "test_lobby"})
    assert response.status_code == 200
    assert "message" in response.json()

def test_join_lobby():
    # Assuming "test_lobby" was created in the previous test
    response = client.post("/lobbies/join", json={"lobby_name": "test_lobby", "player_id": "player1"})
    assert response.status_code == 200
    assert "message" in response.json()

def test_list_lobbies():
    response = client.get("/lobbies/list")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

