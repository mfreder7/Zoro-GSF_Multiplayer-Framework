from .protocols.udp_server import GameServer
from typing import Dict

class UDPManager:
    def __init__(self):
        self.servers: Dict[str, GameServer] = {}

    def create_server(self, lobby_id: str, host: str, port: int):
        if lobby_id in self.servers:
            raise ValueError(f"Lobby {lobby_id} already exists.")
        server = GameServer(host, port)
        self.servers[lobby_id] = server
        server.start()
        print(f"Lobby {lobby_id} created and started.")

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
