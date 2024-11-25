from pydantic import BaseModel

class Player(BaseModel):
    name: str
    id: str
    admin: bool = False
    ready: bool = False
    # a placeholder string that holds any additional data the player is communicating (to test encode/decode)
    data: str = ""
