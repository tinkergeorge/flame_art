#!/usr/bin/env python3

import socket

# this receiver works because it specifies the interface
# ADDRESS = 'localhost'
# this works because inaddr any
ADDRESS = '0.0.0.0'
# this does not work because it doesn't specify an interface
# ADDRESS = '192.168.5.255' 
# this opens a receiver on the interface that receives broadcast and directed
# ADDRESS = '192.168.5.38'

PORT = 10000

def udp_receiver():
    server_address = (ADDRESS, PORT)  # Bind to the same address and port as the sender

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the address and port
    print(f'Starting up on {server_address}')
    sock.bind(server_address)

    while True:
        print('\nWaiting to receive message')
        try: 
            data, address = sock.recvfrom(4096)

            print(f'Received {len(data)} bytes from {address}')
            print(data)
        except socket.error as e:
            print(f' received socket error {e} errno {e.errno} on transmit, recreating socket')
            sock.close()
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(server_address)

        if data:
            try:
                sent = sock.sendto(b'ACK', address)
                print(f'Sent acknowledgment to {address} result {sent}')
            except socket.error as e:
                print(f' sendto threw error {e} continuing')

if __name__ == "__main__":
    udp_receiver()