# reliable.py
import json
import queue
import threading
import time
from typing import Dict, Tuple

from .base_handler import BaseHandler

class ReliableHandler(BaseHandler):
    def __init__(self, sock):
        super().__init__(sock)
        self.sequence_number = 0
        self.pending_acks: Dict[int, Tuple[dict, Tuple[str, int], float]] = {}
        self.ack_lock = threading.Lock()
        self.retry_thread = threading.Thread(target=self.retry_unacknowledged_packets, daemon=True)
        self.retry_thread.start()

    def send(self, packet: dict, address: Tuple[str, int]):
        with self.ack_lock:
            self.sequence_number += 1
            packet["seq"] = self.sequence_number
            encoded_packet = json.dumps(packet).encode('utf-8')
            self.sock.sendto(encoded_packet, address)
            self.pending_acks[self.sequence_number] = (packet, address, time.time())

    def process_queue(self):
        while self.running:
            try:
                packet, address = self.queue.get(timeout=0.1)
                self.send(packet, address)
            except queue.Empty:
                continue

    def process_ack(self, seq_num: int):
        with self.ack_lock:
            self.pending_acks.pop(seq_num, None)

    def retry_unacknowledged_packets(self):
        while self.running:
            with self.ack_lock:
                current_time = time.time()
                for seq_num, (packet, address, timestamp) in list(self.pending_acks.items()):
                    if current_time - timestamp > 1.0:  # ack_timeout
                        encoded_packet = json.dumps(packet).encode('utf-8')
                        self.sock.sendto(encoded_packet, address)
                        self.pending_acks[seq_num] = (packet, address, current_time)
            time.sleep(0.1)

    def stop(self):
        super().stop()
        self.retry_thread.join()