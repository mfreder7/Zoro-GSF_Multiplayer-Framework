import queue
import threading
import time
import json
from typing import Dict, Any

class ReliableHandler:
    def __init__(self, queue: queue.Queue):
        self.sequence_number = 0
        self.ack_timeout = 1.0  # seconds
        self.max_retries = 3
        self.pending_acks: Dict[int, Any] = {}
        self.lock = threading.Lock()
        self.queue = queue

        # Start a thread to monitor pending acknowledgments
        threading.Thread(target=self.retry_unacknowledged_packets, daemon=True).start()

    def send(self, sock, data, address):
        with self.lock:
            self.sequence_number += 1
            packet = {
                "seq": self.sequence_number,
                "data": data,
                "reliable": True
            }
            encoded_packet = json.dumps(packet).encode('utf-8')
            sock.sendto(encoded_packet, address)
            self.pending_acks[self.sequence_number] = {
                "packet": packet,
                "address": address,
                "retries": 0,
                "timestamp": time.time()
            }

    def process_ack(self, seq_num):
        with self.lock:
            seq_num = int(seq_num)
            if seq_num in self.pending_acks:
                del self.pending_acks[seq_num]

    def retry_unacknowledged_packets(self):
        while True:
            with self.lock:
                current_time = time.time()
                to_remove = []
                for seq_num, info in self.pending_acks.items():
                    if current_time - info["timestamp"] > self.ack_timeout:
                        if info["retries"] < self.max_retries:
                            # Resend the packet
                            encoded_packet = json.dumps(info["packet"]).encode('utf-8')
                            sock = info.get("sock")
                            address = info["address"]
                            sock.sendto(encoded_packet, address)
                            info["retries"] += 1
                            info["timestamp"] = current_time
                        else:
                            # Max retries reached, remove from pending_acks
                            to_remove.append(seq_num)
                for seq_num in to_remove:
                    del self.pending_acks[seq_num]
            time.sleep(0.1)
