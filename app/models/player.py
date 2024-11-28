# app/models/player.py
from pydantic import BaseModel

class Player(BaseModel):
    name: str
    id: str
    admin: bool = False
    ready: bool = False
    data: str = ""
