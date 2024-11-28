from .protocols.udp_client import GameServer
from typing import Dict

class UDPManager:
    def __init__(self):
        self.servers: Dict[str, GameServer] = {}

    def create_server(self, lobby_name: str, host: str, port_reliable: int, port_unreliable: int):
        if lobby_name in self.servers:
            raise ValueError(f"Lobby {lobby_name} already exists.")
        server = GameServer(host, port_reliable, port_unreliable)
        self.servers[lobby_name] = server
        print(f"Lobby {lobby_name} created and started. {server.running}")

    def join_server(self, lobby_id: str, player_id: str):
        server = self.servers.get(lobby_id)
        if not server:
            raise ValueError(f"Lobby {lobby_id} does not exist.")
        
        # Make sure player is not already in the lobby
        if player_id in server.clients:
            raise ValueError(f"Player {player_id} is already in lobby {lobby_id}")

        return server.reliable_port, server.unreliable_port

    def remove_server(self, lobby_id: str):
        if lobby_id not in self.servers:
            raise ValueError(f"Lobby {lobby_id} does not exist.")
        server = self.servers.pop(lobby_id)
        server.stop()
        print(f"Lobby {lobby_id} stopped and removed.")


    def stop_all_servers(self):
        for server_id in list(self.servers.keys()):
            self.remove_server(server_id)
        print("All servers stopped and removed.")
