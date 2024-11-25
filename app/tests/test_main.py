from fastapi.testclient import TestClient
# from app.main import app  # Remove this import if not needed

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Game Server API"}