import argparse
import json
import requests
import socket
import threading
import time
from typing import Optional, Dict, List

class UDPTestClient:
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.running = False
        self.reliable_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.unreliable_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sequence = 0
        self.server_ip = None
        self.reliable_port = None
        self.unreliable_port = None
        self.receive_thread = None

    def fetch_lobbies(self, api_url: str) -> List[Dict]:
        try:
            response = requests.get(f"{api_url}/api/lobbies")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching lobbies: {e}")
            return []

    def connect_to_lobby(self, lobby_info: Dict) -> bool:
        self.server_ip = lobby_info['ip']
        self.reliable_port = lobby_info['port_reliable']
        self.unreliable_port = lobby_info['port_unreliable']

        try:
            # Connect reliable socket
            self.reliable_socket.connect((self.server_ip, self.reliable_port))
            
            # Connect unreliable socket
            self.unreliable_socket.connect((self.server_ip, self.unreliable_port))
            
            # Send connect packet on reliable socket
            connect_packet = {
                'type': 'connect',
                'client_id': self.client_id,
                'seq': self.sequence
            }
            self._send_packet(connect_packet, reliable=True)
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def _send_packet(self, packet: dict):
        """Internal method to send a packet"""
        try:
            encoded_packet = json.dumps(packet).encode('utf-8')
            self.reliable_socket.sendto(encoded_packet, (self.server_ip, self.reliable_port))
        except Exception as e:
            print(f"Error sending packet: {e}")

    def _listen_for_packets(self):
        """Internal method to listen for incoming packets"""
        self.reliable_socket.settimeout(1.0)
        while self.running:
            try:
                data, _ = self.reliable_socket.recvfrom(4096)
                packet = json.loads(data.decode('utf-8'))
                self._handle_packet(packet)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error receiving packet: {e}")

    def _handle_packet(self, packet: dict):
        """Handle different packet types"""
        packet_type = packet.get('type')
        client_id = packet.get('client_id')

        if packet_type == 'connect':
            print(f"Client {client_id} connected")
        elif packet_type == 'disconnect':
            print(f"Client {client_id} disconnected")
        elif packet_type == 'update':
            print(f"Update from {client_id}: {packet.get('data')}")
        elif packet_type == 'ack':
            print(f"Received ack for sequence {packet.get('seq')}")

def main():
    parser = argparse.ArgumentParser(description='UDP Test Client')
    parser.add_argument('client_id', help='Unique client identifier')
    parser.add_argument('api_url', help='API URL ie. http://localhost:8000')
    args = parser.parse_args()

    client = UDPTestClient(args.client_id)
    
    lobbies = client.fetch_lobbies(args.api_url)
    if not lobbies:
        print("No lobbies available")
        return

    lobby_info = lobbies[0]  # For simplicity, connect to the first lobby
    if not client.connect_to_lobby(lobby_info):
        print("Failed to connect to lobby")
        return

    client.running = True
    client.receive_thread = threading.Thread(target=client._listen_for_packets, daemon=True)
    client.receive_thread.start()

    print("Commands: update <message>, quit")
    try:
        while True:
            cmd = input("> ").strip().split(maxsplit=1)
            if not cmd:
                continue

            if cmd[0] == "quit":
                break
            elif cmd[0] == "update" and len(cmd) > 1:
                client._send_packet({"type": "update", "client_id": client.client_id, "seq": client.sequence, "data": {"message": cmd[1]}})
            else:
                print("Unknown command")

    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        client.running = False
        client.reliable_socket.close()
        client.unreliable_socket.close()

if __name__ == '__main__':
    main()