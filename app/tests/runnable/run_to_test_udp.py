import socket
import json
import threading
import time

listening = True  # Control flag for the listener thread

def listen_for_packets(sock):
    sock.settimeout(1.0)  # Set a timeout to allow periodic checks
    while listening:
        try:
            data, _ = sock.recvfrom(4097)

            packet = json.loads(data.decode('utf-8'))
            handle_packet(packet)
        except socket.timeout:
            continue  # Timeout occurred, loop back and check if still listening
        except Exception as e:
            print(f"Error receiving packet: {e}")
            break  # Exit the loop on other exceptions

def handle_packet(packet):
    packet_type = packet.get('type')
    if packet_type in ['connect', 'disconnect']:
        print(f"Received {packet_type} packet from server")
    else:
        # Process other packet types without printing
        pass

def main():
    global listening
    server_address = ('127.0.0.1', 4200)  # Adjust to your server's IP and port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    client_id = 'client1'  # Your unique client ID

    # Send a connect packet to the server
    connect_packet = {'type': 'connect', 'client_id': client_id}
    sock.sendto(json.dumps(connect_packet).encode('utf-8'), server_address)

    # Start a thread to listen for incoming packets
    listener_thread = threading.Thread(target=listen_for_packets, args=(sock,), daemon=True)
    listener_thread.start()

    try:
        while True:
            # Send update packets or interact as needed
            update_packet = {'type': 'update', 'client_id': client_id, 'data': 'your data here'}
            sock.sendto(json.dumps(update_packet).encode('utf-8'), server_address)
            time.sleep(1)  # Adjust the frequency as needed
    except KeyboardInterrupt:
        # Send a disconnect packet before exiting
        disconnect_packet = {'type': 'disconnect', 'client_id': client_id}
        sock.sendto(json.dumps(disconnect_packet).encode('utf-8'), server_address)

        # Stop the listener thread and close the socket
        listening = False
        listener_thread.join()
        sock.close()

if __name__ == '__main__':
    main()