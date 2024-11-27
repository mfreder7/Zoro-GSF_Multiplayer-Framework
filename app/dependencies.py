# app/dependencies.py
from fastapi import Request, Depends
from .utils.udp_manager import UDPManager
from typing import Annotated

def get_udp_manager(request: Request) -> UDPManager:
    return request.app.state.udp_manager

UDPManagerDep = Annotated[UDPManager, Depends(get_udp_manager)]