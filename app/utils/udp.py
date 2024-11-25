from protocols.udp_server import GameServer
from protocols.udp_client import GameClient
from typing import Dict

class UDPManager:
    def __init__(self):
        self.servers: Dict[str, GameServer] = {}
        self.clients: Dict[str, GameClient] = {}

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

    def create_client(self, client_id: str, server_host: str, server_port: int):
        if client_id in self.clients:
            raise ValueError(f"Client {client_id} already exists.")
        client = GameClient(server_host, server_port, client_id)
        self.clients[client_id] = client
        client.start()
        print(f"Client {client_id} created and connected to server at {server_host}:{server_port}.")

    def remove_client(self, client_id: str):
        if client_id not in self.clients:
            raise ValueError(f"Client {client_id} does not exist.")
        client = self.clients.pop(client_id)
        client.stop()
        print(f"Client {client_id} stopped and removed.")

# # Example usage
#     manager = UDPManager()

#     # Create a server (lobby)
#     manager.create_server(lobby_id="lobby1", host="127.0.0.1", port=12345)

#     # Create clients (players)
#     manager.create_client(client_id="client1", server_host="127.0.0.1", server_port=12345)
#     manager.create_client(client_id="client2", server_host="127.0.0.1", server_port=12345)

#     # Simulate sending updates
#     manager.clients["client1"].send_update({"position": [1, 2, 3]})
#     manager.clients["client2"].send_update({"position": [4, 5, 6]})

#     # Remove clients and server
#     manager.remove_client("client1")
#     manager.remove_client("client2")
#     manager.remove_server("lobby1")