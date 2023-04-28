import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

expected_seq = 0

while True:
    data, addr = sock.recvfrom(1024)
    received_seq = int(data.decode().split(":")[0])
    print(f"Received packet with sequence number {received_seq}.")
    if received_seq == expected_seq:
        ack = f"ACK:{received_seq}".encode()
        sock.sendto(ack, addr)
        print(f"Sent ACK for packet with sequence number {received_seq}.")
        expected_seq += 1
    else:
        print(f"Received out of order packet with sequence number {received_seq}. Ignoring.")

