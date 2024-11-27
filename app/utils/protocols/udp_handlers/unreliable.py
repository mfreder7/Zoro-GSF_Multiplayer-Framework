# unreliable.py
import json
import queue
from typing import Tuple

from .base_handler import BaseHandler

class UnreliableHandler(BaseHandler):
    def send(self, packet: dict, address: Tuple[str, int]):
        encoded_packet = json.dumps(packet).encode('utf-8')
        self.sock.sendto(encoded_packet, address)

    def process_queue(self):
        while self.running:
            try:
                packet, address = self.queue.get(timeout=0.01)
                self.send(packet, address)
            except queue.Empty:
                continue