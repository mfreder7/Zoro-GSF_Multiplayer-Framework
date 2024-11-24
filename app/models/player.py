from pydantic import BaseModel

class Player(BaseModel):
    name: str
    id: str
    admin: bool = False
    # TODO: implement later for returning the player's current lobby
    # lobby: str = None
