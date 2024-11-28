# game_server.py
import socket
import threading
import json
from typing import Dict, Tuple

from .udp_handlers.reliable import ReliableHandler
from .udp_handlers.unreliable import UnreliableHandler


class GameServer:
    def __init__(self, host: str, reliable_port: int, unreliable_port: int):
        self.host = host
        self.reliable_port = reliable_port
        self.unreliable_port = unreliable_port
        self.running = True
        self.clients: Dict[str, Tuple[str, int]] = {}

        # Initialize sockets
        self.reliable_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.reliable_sock.bind((host, reliable_port))

        self.unreliable_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.unreliable_sock.bind((host, unreliable_port))

        # Initialize handlers and start threads
        self.reliable_handler = ReliableHandler(self.reliable_sock)
        self.unreliable_handler = UnreliableHandler(self.unreliable_sock)

        threading.Thread(target=self.receive_packets, args=(self.reliable_sock, True), daemon=True).start()
        threading.Thread(target=self.receive_packets, args=(self.unreliable_sock, False), daemon=True).start()

    def receive_packets(self, sock, reliable: bool):
        while self.running:
            try:
                data, address = sock.recvfrom(4096)
                packet = json.loads(data.decode('utf-8'))
                self.handle_packet(packet, address, reliable)
            except Exception as e:
                print(f"Error receiving packet: {e}")

    def handle_packet(self, packet: dict, address: Tuple[str, int], reliable: bool):
        packet_type = packet.get("type")

        if packet_type == "connect":
            self.handle_connect(packet, address)
        elif packet_type == "disconnect":
            self.handle_disconnect(packet, address)
        elif packet_type == "update":
            self.handle_update(packet, address)
        elif packet_type == "ack" and reliable:
            seq_num = packet.get("seq")
            self.reliable_handler.process_ack(seq_num)
        else:
            print(f"Unknown packet type: {packet_type}")

    def handle_connect(self, packet: dict, address: Tuple[str, int]):
        client_id = packet.get("client_id")
        self.clients[client_id] = address
        print(f"Client {client_id} connected from {address}")
        # Notify other clients
        self.broadcast(packet, reliable=True)

    def handle_disconnect(self, packet: dict, address: Tuple[str, int]):
        client_id = packet.get("client_id")
        self.clients.pop(client_id, None)
        print(f"Client {client_id} disconnected")
        # Notify other clients
        self.broadcast(packet, reliable=True)
        # Remove client from handlers
        self.reliable_handler.remove_client(client_id)
        # self.unreliable_handler.remove_client(client_id)


    def handle_update(self, packet: dict, address: Tuple[str, int]):
        print(f"Received update from {packet.get('client_id')}")
        self.broadcast(packet, reliable=False)

    def broadcast(self, packet: dict, reliable: bool):
        for address in self.clients.values():
            if reliable:
                self.reliable_handler.enqueue(packet, address)
            else:
                self.unreliable_handler.enqueue(packet, address)


    def stop(self):
        self.running = False
        self.reliable_handler.stop()
        self.unreliable_handler.stop()
        self.reliable_sock.close()
        self.unreliable_sock.close()
