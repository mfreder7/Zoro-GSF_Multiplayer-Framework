# app/models/lobby.py
from typing import List
from pydantic import BaseModel
from .player import Player

class Lobby(BaseModel):
    name: str
    id: str
    ip: str
    port_reliable: int
    port_unreliable: int
    players: List[Player] = []