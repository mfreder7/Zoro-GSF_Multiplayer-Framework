from typing import List
from pydantic import BaseModel
from .player import Player

class Lobby(BaseModel):
    name: str
    id: str
    players: List[Player] = []