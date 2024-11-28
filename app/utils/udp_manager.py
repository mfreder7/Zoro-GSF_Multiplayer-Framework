import socket
import time
import threading
from .protocols.udp_client import GameServer
from typing import Dict, Set, Tuple

class UDPManager:
    def __init__(self):
        self.servers: Dict[str, GameServer] = {}
        self.used_ports: Set[int] = set()
        self.lobby_admins: Dict[str, str] = {}  # Maps lobby_name to admin_id
        self.host = '0.0.0.0'  # Bind to all interfaces (to be replaced)
        self.interface = '127.0.0.1'  # Bind to a specific interface (localhost for example)
        self.last_activity: Dict[str, float] = {}  # Track last activity time per lobby
        self.cleanup_thread = threading.Thread(target=self._cleanup_inactive_lobbies, daemon=True)
        self.running = True
        self.cleanup_thread.start()

    def _cleanup_inactive_lobbies(self):
        """Background thread to cleanup empty lobbies after a timeout"""
        EMPTY_LOBBY_TIMEOUT = 300  # 5 minutes in seconds
        
        while self.running:
            current_time = time.time()
            
            # Check each lobby's player count
            for lobby_id in list(self.servers.keys()):
                server = self.servers.get(lobby_id)
                if server and not server.clients:  # Empty lobby
                    # Only track time when lobby becomes empty
                    if lobby_id not in self.last_activity:
                        self.last_activity[lobby_id] = current_time
                    elif current_time - self.last_activity[lobby_id] > EMPTY_LOBBY_TIMEOUT:
                        print(f"Removing empty lobby {lobby_id}")
                        self.remove_server(lobby_id)
                else:
                    # Lobby has players, remove from tracking
                    self.last_activity.pop(lobby_id, None)
            
            # Check every 30 seconds
            time.sleep(30)

    def find_free_port(self) -> int:
        """Find an available non-reserved port."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind((self.interface, 0))  # Bind to a specific interface and let the OS assign an available port
            port = s.getsockname()[1]
            # Ensure the port is not already used in the manager
            while port in self.used_ports:
                s.bind((self.interface, 0))
                port = s.getsockname()[1]
            return port

    def create_server(self, lobby_name: str, admin_id: str):
        """Create a new game server for a lobby.
        
        Args:
            lobby_name: Name/ID of the lobby
            admin_id: ID of the player who will be admin
        """
        if lobby_name in self.servers:
            raise ValueError(f"Lobby {lobby_name} already exists.")

        # Find free ports for reliable and unreliable sockets
        port_reliable = self.find_free_port()
        self.used_ports.add(port_reliable)

        port_unreliable = self.find_free_port()
        self.used_ports.add(port_unreliable)
        print(f"Found free ports: {port_reliable} (reliable), {port_unreliable} (unreliable)")

        # Create server bound to all interfaces
        server = GameServer(self.host, port_reliable, port_unreliable)
        self.servers[lobby_name] = server
        self.lobby_admins[lobby_name] = admin_id
        self.last_activity[lobby_name] = time.time()
        
        print(f"Lobby {lobby_name} created and started on ports {port_reliable} (reliable), {port_unreliable} (unreliable)")

    def join_server(self, lobby_id: str, player_id: str) -> Tuple[int, int]:
        """Join a player to a server, setting admin status if they're the creator.
        
        Args:
            lobby_id: The lobby to join
            player_id: The joining player's ID
        
        Returns:
            Tuple of (reliable_port, unreliable_port)
        """
        server = self.servers.get(lobby_id)
        if not server:
            raise ValueError(f"Lobby {lobby_id} does not exist.")
        
        # Check if player is already in the lobby
        if player_id in server.clients:
            raise ValueError(f"Player {player_id} is already in lobby {lobby_id}")

        # Set admin status if this player created the lobby
        is_admin = self.lobby_admins.get(lobby_id) == player_id
        
        # Update last activity when player joins
        self.last_activity[lobby_id] = time.time()
        
        # The actual connection will happen via UDP after getting these ports
        return server.reliable_port, server.unreliable_port

    def update_activity(self, lobby_id: str):
        """Update the last activity timestamp for a lobby"""
        if lobby_id in self.servers:
            self.last_activity[lobby_id] = time.time()

    def remove_server(self, lobby_id: str):
        """Remove a server and clean up its resources."""
        server = self.servers.pop(lobby_id, None)
        if server:
            self.used_ports.discard(server.reliable_port)
            self.used_ports.discard(server.unreliable_port)
            self.lobby_admins.pop(lobby_id, None)
            self.last_activity.pop(lobby_id, None)
            server.stop()
            print(f"Lobby {lobby_id} stopped and removed.")
        else:
            raise ValueError(f"Lobby {lobby_id} does not exist.")

    def stop_all_servers(self):
        """Stop all servers and cleanup thread."""
        self.running = False
        if self.cleanup_thread.is_alive():
            self.cleanup_thread.join()
        for server_id in list(self.servers.keys()):
            self.remove_server(server_id)
        print("All servers stopped and removed.")
