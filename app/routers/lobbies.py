from fastapi import APIRouter, HTTPException
from ..models.lobby import Lobby
from ..models.player import Player

router = APIRouter()

# TODO: Migrate to a rt db later. For now, use a locally stored list of lobbies
lobbies: list[Lobby] = []

@router.post("/create", tags=["lobbies"])
async def create_lobby(lobby_name: str) -> Lobby:
    if lobby_name in lobbies:
        raise HTTPException(status_code=400, detail="Lobby already exists")
    lobbies[lobby_name] = {"players": []}
    return {"message": f"Lobby '{lobby_name}' created"}

@router.post("/join", tags=["lobbies"])
async def join_lobby(lobby_name: str, player_id: str) -> Lobby:
    if lobby_name not in lobbies:
        raise HTTPException(status_code=404, detail="Lobby not found")
    lobbies[lobby_name]["players"].append(player_id)
    return {"message": f"Player '{player_id}' joined lobby '{lobby_name}'"}

@router.post("/lobbies/leave", tags=["lobbies"])
async def leave_lobby(lobby_id: str, player_id: str) -> bool:
    # TODO: implement lobby leave logic
    pass

@router.get("/list", tags=["lobbies"])
async def list_lobbies() -> list[Lobby]:
    return lobbies
