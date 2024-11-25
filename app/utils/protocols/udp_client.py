import socket
import threading
import json

class GameClient:
    def __init__(self, server_host: str, server_port: int, client_id: str):
        self.server_address = (server_host, server_port)
        self.client_id = client_id
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = True

    def start(self):
        threading.Thread(target=self.receive_packets).start()
        self.send_connect()

    def stop(self):
        self.running = False
        self.send_disconnect()
        self.sock.close()
        print("Client stopped")

    def send_connect(self):
        packet = {
            "type": "connect",
            "client_id": self.client_id
        }
        self.sock.sendto(json.dumps(packet).encode('utf-8'), self.server_address)

    def send_disconnect(self):
        packet = {
            "type": "disconnect",
            "client_id": self.client_id
        }
        self.sock.sendto(json.dumps(packet).encode('utf-8'), self.server_address)

    def send_update(self, data: dict):
        packet = {
            "type": "update",
            "client_id": self.client_id,
            "data": data
        }
        self.sock.sendto(json.dumps(packet).encode('utf-8'), self.server_address)

    def receive_packets(self):
        while self.running:
            try:
                data, _ = self.sock.recvfrom(1024)
                packet = json.loads(data.decode('utf-8'))
                self.handle_packet(packet)
            except Exception as e:
                print(f"Error receiving packet: {e}")

    def handle_packet(self, packet: dict):
        packet_type = packet.get("type")
        if packet_type == "update":
            self.handle_update(packet)
        else:
            print(f"Unknown packet type: {packet_type}")

    def handle_update(self, packet: dict):
        client_id = packet.get("client_id")
        data = packet.get("data")
        print(f"Received update from {client_id}: {data}")