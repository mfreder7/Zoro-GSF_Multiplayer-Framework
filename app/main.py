from fastapi import FastAPI, Depends
from typing import List

from fastapi.concurrency import asynccontextmanager
from .routers import lobbies, players
from .utils.udp_manager import UDPManager

udp_manager:UDPManager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize UDPManager
    print("Starting UDP Manager...")
    udp_manager = UDPManager()
    app.state.udp_manager = udp_manager
    
    yield
    
    # Shutdown: Clean up UDPManager
    print("Shutting down UDP Manager...")
    udp_manager.stop_all_servers()

app = FastAPI(lifespan=lifespan)

app.include_router(
    lobbies.router,
    prefix="/lobbies",
    tags=["lobbies"],
)

app.include_router(
    players.router,
    prefix="/players",
    tags=["players"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Game Server API"}