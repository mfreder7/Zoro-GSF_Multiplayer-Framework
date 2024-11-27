import socket
import threading
import json
import queue
from typing import Dict, Tuple

from app.utils.protocols.udp_handlers.reliable import ReliableHandler
from app.utils.protocols.udp_handlers.unreliable import UnreliableHandler

class GameServer:
    def __init__(self, host: str, reliable_port: int, unreliable_port: int):
        # Addresses for reliable and unreliable sockets
        self.reliable_address = (host, reliable_port)
        self.unreliable_address = (host, unreliable_port)
        self.clients: Dict[str, Tuple[str, int]] = {}
        self.running = True

        # Initialize separate sockets for reliable and unreliable messages
        self.reliable_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.unreliable_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.reliable_sock.bind(self.reliable_address)
        self.unreliable_sock.bind(self.unreliable_address)

        # Separate queues for reliable and unreliable messages
        self.reliable_queue = queue.Queue()
        self.unreliable_queue = queue.Queue()

        # Initialize handlers without socket locks
        self.reliable_handler = ReliableHandler(self.reliable_queue)
        self.unreliable_handler = UnreliableHandler(self.unreliable_queue)

    def start(self):
        print(f"Server started at {self.reliable_address} (reliable) and {self.unreliable_address} (unreliable)")
        # Start receiver threads
        threading.Thread(target=self.receive_reliable_packets, daemon=True).start()
        threading.Thread(target=self.receive_unreliable_packets, daemon=True).start()
        # Start sender threads
        threading.Thread(target=self.reliable_sender, daemon=True).start()
        threading.Thread(target=self.unreliable_sender, daemon=True).start()

    def stop(self):
        self.running = False
        self.reliable_sock.close()
        self.unreliable_sock.close()
        print("Server stopped")

    def receive_reliable_packets(self):
        while self.running:
            try:
                data, address = self.reliable_sock.recvfrom(1024)
                packet = json.loads(data.decode('utf-8'))
                self.handle_packet(packet, address, reliable=True)
            except Exception as e:
                print(f"Error receiving reliable packet: {e}")

    def receive_unreliable_packets(self):
        while self.running:
            try:
                data, address = self.unreliable_sock.recvfrom(1024)
                packet = json.loads(data.decode('utf-8'))
                self.handle_packet(packet, address, reliable=False)
            except Exception as e:
                print(f"Error receiving unreliable packet: {e}")

    def handle_packet(self, packet: dict, address: Tuple[str, int], reliable: bool):
        if reliable:
            # Handle reliable packet with acknowledgment
            seq_num = packet.get("seq")
            self.send_ack(seq_num, address)
            packet_data = packet.get("data", {})
            packet_type = packet_data.get("type")
        else:
            # Handle unreliable packet directly
            packet_type = packet.get("type")

        if packet_type == "connect":
            self.handle_connect(packet, address)
        elif packet_type == "disconnect":
            self.handle_disconnect(packet, address)
        elif packet_type == "update":
            self.handle_update(packet, address)
        elif packet_type == "ack":
            # Process acknowledgment for reliable messages
            seq_num = packet.get("seq")
            self.reliable_handler.process_ack(seq_num)
        else:
            print(f"Unknown packet type: {packet_type}")

        # Broadcast new connect or disconnect to all clients
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
        self.send_to_all_clients(packet, reliable=False)

    def update_when_connect_or_disconnect(self, client_id: str, action: str):
        packet = {
            "type": action,
            "client_id": client_id
        }
        self.send_to_all_clients(packet, reliable=True)

    def send_to_all_clients(self, packet: dict, reliable: bool = False):
        for client_id, address in self.clients.items():
            self.send_packet(packet, address, reliable=reliable)

    def send_packet(self, packet: dict, address: Tuple[str, int], reliable: bool = False):
        if reliable:
            self.reliable_queue.put((packet, address))
        else:
            self.unreliable_queue.put((packet, address))

    def send_ack(self, seq_num: int, address: Tuple[str, int]):
        ack_packet = {
            "type": "ack",
            "seq": seq_num
        }
        encoded_packet = json.dumps(ack_packet).encode('utf-8')
        self.reliable_sock.sendto(encoded_packet, address)

    def reliable_sender(self):
        while self.running:
            try:
                packet, address = self.reliable_queue.get(timeout=0.1)
                self.reliable_handler.send(self.reliable_sock, packet, address)
            except queue.Empty:
                continue

    def unreliable_sender(self):
        while self.running:
            try:
                packet, address = self.unreliable_queue.get(timeout=0.01)  # Shorter timeout for unreliable
                self.unreliable_handler.send(self.unreliable_sock, packet, address)
            except queue.Empty:
                continue

# Example usage:
# if __name__ == "__main__":
#     server = GameServer(host='localhost', reliable_port=9000, unreliable_port=9001)
#     server.start()
#     try:
#         while True:
#             pass  # Keep the main thread alive
#     except KeyboardInterrupt:
#         server.stop()
