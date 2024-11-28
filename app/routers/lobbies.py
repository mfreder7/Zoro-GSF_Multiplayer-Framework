from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, List

from app.utils.protocols.udp_client import GameServer
from ..models.lobby import Lobby
from ..models.player import Player
from ..utils.udp_manager import UDPManager
from ..dependencies import get_udp_manager, UDPManagerDep
from pydantic import BaseModel

router = APIRouter()

# Response models
class MessageResponse(BaseModel):
    message: str

class JoinResponse(BaseModel):
    lobby: Lobby
    player: Player

class LobbyListResponse(BaseModel):
    lobbies: List[Lobby]
    

# Dependency for varifying lobby name isn't already take (TODO: expand to check for game account ID in the future)
@router.post("/create", status_code=201)
async def create_lobby(lobby_name, player_id, udp_manager: UDPManagerDep):
    udp_manager.create_server(lobby_name, player_id)
    return {"message": f"Lobby '{lobby_name}' created successfully."}

@router.post("/join", response_model=MessageResponse)
async def join_lobby(
    lobby_name: str,
    player_id: str,
    udp_manager: UDPManagerDep
) -> MessageResponse:
    if udp_manager.servers.get(lobby_name, {}) == {}:
        raise HTTPException(status_code=404, detail="Lobby not found")
    
    player = Player(name=player_id, id=player_id)

    if udp_manager.servers[lobby_name]:
        server_ports = udp_manager.join_server(lobby_id=lobby_name, player_id=player_id)
        # Update activity when player joins
        udp_manager.update_activity(lobby_name)
        return MessageResponse(message=f"p{server_ports[0]}|{server_ports[1]}l")
    

# TODO: measure what methods perform better for disconnecting. Right now we have safe socket disconnecting

# @router.post("/leave", response_model=MessageResponse)
# async def leave_lobby(
#     lobby_id: str,
#     player_id: str,
#     udp_manager: UDPManagerDep
# ) -> MessageResponse:
#     if lobby_id not in lobbies:
#         raise HTTPException(status_code=404, detail="Lobby not found")
    
#     lobby = lobbies[lobby_id]
#     lobby.players = [p for p in lobby.players if p.id != player_id]
    
    # return MessageResponse(message=f"Player '{player_id}' left lobby '{lobby_id}'")

# lobbies.py
@router.get("/list", response_model=List[Lobby])
async def list_lobbies(udp_manager: UDPManagerDep) -> List[Lobby]:
    lobbies = []
    for lobby_name, server in udp_manager.servers.items():
        lobby = Lobby(
            name=lobby_name,
            id=lobby_name,  # Assuming lobby ID is the same as the name
            ip=server.host,  # Accessing the host attribute here
            port_reliable=server.reliable_port,
            port_unreliable=server.unreliable_port,
            players=[Player(name=pid, id=pid) for pid in server.clients.keys()]
        )
        lobbies.append(lobby)
    return lobbies
