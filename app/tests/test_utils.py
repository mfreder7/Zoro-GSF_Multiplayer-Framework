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
