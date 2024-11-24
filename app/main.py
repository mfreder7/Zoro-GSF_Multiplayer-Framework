from fastapi import FastAPI, WebSocket
from typing import List
from .routers import lobbies, players

app = FastAPI()

app.include_router(
    lobbies.router,
    prefix="/lobbies",
    tags=["lobbies"]
)

app.include_router(
    players.router,
    prefix="/players",
    tags=["players"]
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Game Server API"}