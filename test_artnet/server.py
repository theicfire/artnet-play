import socket

# Art-Net constants
ART_NET_PORT = 6454
ART_NET_HEADER = b'Art-Net\x00'

def receive_artnet_data():
    # Create a UDP socket and bind it to listen on any address on the Art-Net port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', ART_NET_PORT))
    print(f"Listening for Art-Net data on port {ART_NET_PORT}...")

    while True:
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        if data.startswith(ART_NET_HEADER):
            # Extracting the opcode (OpOutput) and universe data
            opcode = data[8:10]
            if opcode == b'\x00P':  # Check for OpOutput (0x5000)
                universe = data[14] + 256 * data[15]  # Little-endian to integer
                dmx_data = data[18:]
                print(f"Received Art-Net data from {addr[0]}:{addr[1]} for Universe {universe}:")
                print(list(dmx_data))

if __name__ == "__main__":
    receive_artnet_data()
