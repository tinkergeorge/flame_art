#!/usr/bin/env python3

# quick test of transmitting UDP packets and seeing what failures you get
# in certain cases and testing IP multicast

import socket

BROADCAST = False

# ADDRESS = 'localhost'
# ADDRESS = '127.0.0.1'
# this works even with broadcast enabled, no checking that it's not a broadcast address
# ADDRESS = '192.168.5.38'
# this works because it's the subnet broadcast address
ADDRESS = '192.168.5.255'


PORT = 10000

def udp_sender():
    server_address = (ADDRESS, PORT)  # Server address and port
    message = b'This is a UDP message'

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if BROADCAST:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    try:
        # Send the message
        while True:
            try:
                print(f'Sending message: {message}')
                sent = sock.sendto(message, server_address)
                print(f'socket sent result {sent}')
            except socket.error as e:
                print(f'socket sendto error {e}')
    finally:
        print('Closing socket')
        sock.close()

if __name__ == "__main__":
    udp_sender()