from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, List
from ..models.lobby import Lobby
from ..models.player import Player
from ..utils.udp_manager import UDPManager
from ..dependencies import get_udp_manager, UDPManagerDep
from pydantic import BaseModel

router = APIRouter()

# Response models
class MessageResponse(BaseModel):
    message: str

# In-memory storage for lobbies
lobbies: Dict[str, Lobby] = {}

@router.post("/create", response_model=MessageResponse)
async def create_lobby(
    lobby_name: str,
    udp_manager: UDPManagerDep
) -> MessageResponse:
    if lobby_name in lobbies:
        raise HTTPException(status_code=400, detail="Lobby already exists")
    
    udp_manager.create_server(lobby_id=lobby_name, host="127.0.0.1", port=12345)
    lobbies[lobby_name] = Lobby(name=lobby_name, id=lobby_name, players=[])
    return MessageResponse(message=f"Lobby '{lobby_name}' created")

@router.post("/join", response_model=MessageResponse)
async def join_lobby(
    lobby_name: str,
    player_id: str,
    udp_manager: UDPManagerDep
) -> MessageResponse:
    if lobby_name not in lobbies:
        raise HTTPException(status_code=404, detail="Lobby not found")
    
    player = Player(name=player_id, id=player_id)
    lobbies[lobby_name].players.append(player)
    
    return MessageResponse(message=f"Player '{player_id}' joined lobby '{lobby_name}'")

@router.post("/leave", response_model=MessageResponse)
async def leave_lobby(
    lobby_id: str,
    player_id: str,
    udp_manager: UDPManagerDep
) -> MessageResponse:
    if lobby_id not in lobbies:
        raise HTTPException(status_code=404, detail="Lobby not found")
    
    lobby = lobbies[lobby_id]
    lobby.players = [p for p in lobby.players if p.id != player_id]
    
    return MessageResponse(message=f"Player '{player_id}' left lobby '{lobby_id}'")

@router.get("/list", response_model=list[Lobby])
async def list_lobbies() -> list[Lobby]:
    return list(lobbies.values())
