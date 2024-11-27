import json
import queue

class UnreliableHandler:
    def __init__(self, queue: queue.Queue):
        self.queue = queue

    def send(self, sock, data, address):
        packet = {
            "type": data.get("type"),
            "client_id": data.get("client_id"),
            "data": data.get("data"),
            "reliable": False
        }
        encoded_packet = json.dumps(packet).encode('utf-8')
        sock.sendto(encoded_packet, address)
