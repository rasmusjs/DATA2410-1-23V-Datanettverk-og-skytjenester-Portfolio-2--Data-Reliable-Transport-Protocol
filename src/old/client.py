import socket
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
MESSAGE = "Hei på deg din gamle sjokolade.

Lorem ipsum dolor sit amet consectetur adipisicing elit. Maxime mollitia,
molestiae quas vel sint commodi repudiandae consequuntur voluptatum laborum
numquam blanditiis harum quisquam eius sed odit fugiat iusto fuga praesentium
optio, eaque rerum! Provident similique accusantium nemo autem. Veritatis
obcaecati tenetur iure eius earum ut molestias architecto voluptate aliquam
nihil, eveniet aliquid culpa officia aut! Impedit sit sunt quaerat, odit,
tenetur error, harum nesciunt ipsum debitis quas aliquid. Reprehenderit,
quia. Quo neque error repudiandae fuga? Ipsa laudantium molestias eos
sapiente officiis modi at sunt excepturi expedita sint? Sed quibusdam
recusandae alias error harum maxime adipisci amet laborum. Perspiciatis
minima nesciunt dolorem! Officiis iure rerum voluptates a cumque velit
quibusdam sed amet tempora. Sit laborum ab, eius fugit doloribus tenetur
fugiat, temporibus enim commodi iusto libero magni deleniti quod quam
consequuntur! Commodi minima excepturi repudiandae velit hic maxime
doloremque. Quaerat provident commodi consectetur veniam similique ad
earum omnis ipsum saepe, voluptas, hic voluptates pariatur est explicabo
fugiat, dolorum eligendi quam cupiditate excepturi mollitia maiores labore
suscipit quas? Nulla, placeat. Voluptatem quaerat non architecto ab laudantium
modi minima sunt esse temporibus sint culpa, recusandae aliquam numquam
totam ratione voluptas quod exercitationem fuga. Possimus quis earum veniam
quasi aliquam eligendi, placeat qui corporis!


Slutt!".encode()
TIMEOUT = 0.5  # in seconds

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def stop_and_wait():
    seq = 0
    while True:
        packet = f"{seq}:{MESSAGE.decode()}"
        sock.sendto(packet.encode(), (UDP_IP, UDP_PORT))
        print(f"Sent packet with sequence number {seq}.")
        sock.settimeout(TIMEOUT)
        try:
            ack, addr = sock.recvfrom(1024)
            ack_seq = int(ack.decode().split(":")[1])
            if ack.decode().startswith("ACK") and ack_seq == seq:
                print(f"Received ACK for packet with sequence number {seq}.")
                seq += 1
                return True
            else:
                print("Received invalid ACK. Ignoring.")
        except socket.timeout:
            print(f"Timeout occurred for packet with sequence number {seq}. Resending.")
            continue

stop_and_wait()

