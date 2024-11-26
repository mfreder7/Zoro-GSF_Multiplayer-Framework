import socket
import threading
import json
from typing import Dict, Tuple

class GameServer:
    def __init__(self, host: str, port: int):
        self.server_address = (host, port)
        self.clients: Dict[str, Tuple[str, int]] = {}
        # socket.AF_INET specifies IPv4, and socket.SOCK_DGRAM specifies the use of UDP.
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.server_address)
        self.running = True

    def start(self):
        print(f"Server started at {self.server_address}")
        threading.Thread(target=self.receive_packets).start()

    def stop(self):
        self.running = False
        self.sock.close()
        print("Server stopped")

    def receive_packets(self):
        while self.running:
            try:
                data, address = self.sock.recvfrom(1024)
                packet = json.loads(data.decode('utf-8'))
                self.handle_packet(packet, address)
            except Exception as e:
                print(f"Error receiving packet: {e}")

    def handle_packet(self, packet: dict, address: Tuple[str, int]):
        packet_type = packet.get("type")
        if packet_type == "connect":
            self.handle_connect(packet, address)
        elif packet_type == "disconnect":
            self.handle_disconnect(packet, address)
        elif packet_type == "update":
            self.handle_update(packet, address)
        else:
            print(f"Unknown packet type: {packet_type}")
        
        # broadcast new connect or disconnect to all clients
        if packet_type in ["connect", "disconnect"]:
            client_id = packet.get("client_id")
            action = "connect" if packet_type == "connect" else "disconnect"
            self.update_when_connect_or_disconnect(client_id, action)

    def handle_connect(self, packet: dict, address: Tuple[str, int]):
        client_id = packet.get("client_id")
        self.clients[client_id] = address
        print(f"Client {client_id} connected from {address}")

    def handle_disconnect(self, packet: dict, address: Tuple[str, int]):
        client_id = packet.get("client_id")
        if client_id in self.clients:
            del self.clients[client_id]
            print(f"Client {client_id} disconnected")

    def handle_update(self, packet: dict, address: Tuple[str, int]):
        client_id = packet.get("client_id")
        data = packet.get("data")
        print(f"Received update from {client_id}: {data}")
        self.send_to_all_clients(packet)

    def update_when_connect_or_disconnect(self, client_id: str, action: str):
        packet = {
            "type": action,
            "client_id": client_id
        }
        self.send_to_all_clients(packet)

    def send_to_all_clients(self, packet: dict):
        for client_id, address in self.clients.items():
            self.sock.sendto(json.dumps(packet).encode('utf-8'), address)