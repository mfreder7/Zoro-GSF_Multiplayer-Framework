# base_handler.py
import queue
import threading
from abc import ABC, abstractmethod
from typing import Tuple


class BaseHandler(ABC):
    def __init__(self, sock):
        self.sock = sock
        self.queue = queue.Queue()
        self.running = True
        self.thread = threading.Thread(target=self.process_queue, daemon=True)
        self.thread.start()

    @abstractmethod
    def send(self, packet: dict, address: Tuple[str, int]):
        pass

    def enqueue(self, packet: dict, address: Tuple[str, int]):
        self.queue.put((packet, address))

    @abstractmethod
    def process_queue(self):
        pass

    def stop(self):
        self.running = False
        self.thread.join()