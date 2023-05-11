import argparse
import random
import socket
import threading
import time
import re
import sys
import os
import struct
import math
import subprocess  # For running commands in the terminal


# Description:
#   Function for getting the interface name, used for adding the network emulation (loss, delay reordering) to the interface
# Global variables:
#   none
# Returns:
#   Returns the interface name as a string
def get_iface():
    cmd = "route | awk 'NR==3{print $NF}'"  # Get the inferface name from the second line and last element of the output of the command "route"
    return subprocess.check_output(cmd, shell=True).decode('utf-8').strip()


# Description:
#   Function for removing the network emulation (loss, delay reordering) from the interface
# Global variables:
#   none
# Returns:
#   none
def remove_artificial_testcase():
    # Get interface name
    interface = get_iface()
    print(f"Removing old Interface: {interface}")
    # Remove the existing qdisc
    subprocess.run(["tc", "qdisc", "del", "dev", interface, "root"])


# Description:
#   Function for adding the network emulation (loss, delay reordering) to the interface
# Parameters:
#   test_case: The test case to run (skip_ack, skip_seq, reorder)
# Global variables:
#   none
# Returns:
#   none
def run_artificial_testcase(test_case=None):
    # Get interface name
    interface = get_iface()
    print(f"Interface: {interface}")

    # Remove the existing qdisc
    # subprocess.run(["tc", "qdisc", "del", "dev", "h3-eth0", "root"])
    # Add a new qdisc with 10% packet loss
    # subprocess.run(["tc", "qdisc", "add", "dev", "h3-eth0", "root", "netem", "loss", "10%"])
    # print("Packet loss added for server side")

    # Remove the existing qdisc
    subprocess.run(["tc", "qdisc", "del", "dev", interface, "root"])

    if test_case == "skip_ack":
        # Add a new qdisc with 10% packet loss for the outgoing packets
        subprocess.run(["tc", "qdisc", "add", "dev", interface, "root", "netem", "loss", "10%"])
        print("Running with skip_ack test case")
    if test_case == "skip_seq":
        # Emulate 5% packet reordering for the outgoing packets for to simulate out of order packets
        subprocess.run(["tc", "qdisc", "add", "dev", interface, "root", "netem", "delay", "50ms", "reorder", "5%"])
        print("Running with skip_seq test case")

    cmd = "tc qdisc show dev " + interface + " root"
    print(subprocess.check_output(cmd, shell=True).decode('utf-8').strip())
    # Add a new qdisc with 10% packet loss
    # subprocess.run(["tc", "qdisc", "add", "dev", interface, "root", "netem", "loss", "10%"])

    # Emulate 5% packet reordering
    # subprocess.run(["tc", "qdisc", "add", "dev", interface, "root", "netem", "delay", "50ms", "reorder", "5%"])

    # Emulate 2% duplicate packets
    # subprocess.run(["tc", "qdisc", "add", "dev", interface, "root", "netem", "duplicate", "2%"])


# Default values
formatting_line = "-" * 45  # Formatting line = -----------------------------
default_server_save_path = "received_files"  # Path to the folder where received files are stored
default_ip = "127.0.0.1"
default_port = 8088


# Description:
#   Function for printing error messages, to standard error output with formatting
# Global variables:
#   error_message: string with the error message to print
# Returns:
#   nothing, it prints the error message with red color and "Error" to standard error output
def print_error(error_message):
    print(f"\033[1;31;1mError: \n\t{error_message}\n\033[0m", file=sys.stderr)


# Description:
#  Function for parsing the flags
# Parameters:
#   flags: holds the flags
# Returns:
#   Returns the flags as a tuple
def parse_flags(flags):
    syn = flags & (1 << 3)  # 1 << 3 = 1000 # 8
    ack = flags & (1 << 2)  # 1 << 2 = 0100 # 4
    fin = flags & (1 << 1)  # 1 << 1 = 0010 # 2
    rst = flags & (1 << 0)  # 1 << 0 = 0001 # 1
    return syn, ack, fin, rst


# Description:
#  Function for setting the flags
# Parameters:
#   syn: holds the syn flag
#   ack: holds the ack flag
#   fin: holds the fin flag
#   rst: holds the rst flag
# Returns:
#   Returns the flags as an integer (byte), for example,
#   if we have syn = 1, ack = 1, fin = 0, rst = 0 then the function returns 12
def set_flags(syn, ack, fin, rst):
    flags = 0
    if syn:
        flags |= (1 << 3)  # 1 << 3 = 1000
    if ack:
        flags |= (1 << 2)  # 1 << 2 = 0100
    if fin:
        flags |= (1 << 1)  # 1 << 1 = 0010
    if rst:
        flags |= (1 << 0)  # 1 << 0 = 0001
    return flags


# Description:
#  Function for printing the flags in a more readable way
# Parameters:
#   flags: holds the flags
# Returns:
#   Returns nothing, it prints the flags e.g "Flags: syn ack"
def pretty_flags(flags):
    syn, ack, fin, rst = parse_flags(flags)
    if syn != 0 or ack != 0 or fin != 0 or rst != 0:
        print(
            f"Flags: {'syn' if syn else ''}{'ack' if ack else ''}{'fin' if fin else ''}{'rst' if rst else ''}")
    else:
        print("Flags: 0")


# Define the structure of the headed
# I = 32 bits, H = 16 bits
# Sequence Number:32 bits, Acknowledgment Number:32, Flags:16 ,Window:16
# From https://docs.python.org/3/library/struct.html
DRTP_struct = struct.Struct("!IIHH")


# Description:
#  Function for creating a header with the right format with fixed bit sizes
# Parameters:
#   sequence_number: holds the sequence number
#   acknowledgment_number: holds the acknowledgment number
#   flags: holds the flags
#   window: holds the window
# Returns:
#   Returns the header as a byte string
def encode_header(sequence_number, acknowledgment_number, flags, window):
    # Sequence Number:32 bits, Acknowledgment Number:32bits, Flags:16bits, Window:16bits
    return DRTP_struct.pack(sequence_number, acknowledgment_number, flags, window)


# Description:
#  Function for parsing a header
# Parameters:
#   header: holds the header
# Returns:
#   Returns the header as a tuple
def decode_header(header):
    return DRTP_struct.unpack(header)


# Description:
#  Function for stripping the header from the packet
# Parameters:
#   raw_data: holds the packet
# Returns:
#   Returns the header as a tuple
def strip_packet(raw_data):
    # Get header from the packet (first 12 bytes)
    header = raw_data[:12]
    # Unpack the header fields
    sequence_number, acknowledgment_number, flags, receiver_window = decode_header(header)
    # Keep only the raw_data from the packet (after the header)
    data = raw_data[12:]
    # Return the header fields and the raw_data decoded as a tuple
    return sequence_number, acknowledgment_number, flags, receiver_window, data


def create_packet(sequence_number, acknowledgment_number, flags, window, data):
    header = encode_header(sequence_number, acknowledgment_number, flags, window)
    return header + data


# Description:
#  Handles a client connection, receives a file from the client and saves it to the save path folder
# Parameters:
#   sock: holds the socket
#   save_path: holds the save path
# Returns:
#   None
def server_handle_client(sock, save_path):
    pass
    """
    # Receive filename and filesize (this is supposed to be the header)
    raw_data, address = sock.recvfrom(1024)
    filename, filesize = raw_data.decode().split(':')  # Extract filename and filesize
    filesize = int(filesize)
    basename = os.path.basename(filename)  # Extract filename from the path
    i = 1  # Counter for duplicate filenames

    # Check if a file exists on the server (in the save path folder) and add a number to the end if it does
    while os.path.exists(os.path.join(save_path, basename)):
        # Split the filename and add a number to the end
        basename = f"{os.path.splitext(basename)[0]}_{i}{os.path.splitext(basename)[1]}"
        i += 1
    print(f'Receiving file {basename}')

    received_bytes = 0  # Counter for received bytes

    # Fjern kommentarer for å lagre til fil, dette er kun for testing
    # with open(os.path.join(save_path, basename), 'wb') as f:
    while received_bytes < filesize:
        # Receive raw_data
        raw_data, address = sock.recvfrom(1024)
        print(raw_data.decode())
        # Fjern kommentarer for å lagre til fil, dette er kun for testing
        # f.write(raw_data) # Write raw_data to file
        received_bytes += len(raw_data)"""


def read_file(filename):
    return open(filename, 'rb')


def close_server_connection(sock, address, sequence_number, receiver_window):
    # If we receive the FIN from the client, send an ACK
    print("Received FIN from the client")
    acknowledgment_number = sequence_number + 1
    flags = set_flags(0, 1, 1, 0)  # Set the ACK flag
    packet = encode_header(sequence_number, acknowledgment_number, flags, receiver_window)
    sock.sendto(packet, address)
    print("Sent FIN ACK to the client")
    # Close the connection on the
    sock.close()


# Description:
#   Create a random initial sequence number for the three-way handshake
# Parameters:
#   None
# Returns:
#   Returns a random initial sequence number as an integer
def random_isn():
    return random.randint(0, 2 ** 32 - 1)


def stop_and_wait(sock, address, sequence_number, acknowledgment_number, flags, receiver_window, packets=None):
    print("Stop and wait")
    # If we are the server, packet_to_send is None
    # If we are the client, we have packets to send (not None)
    # We are the client
    if packets is not None:
        # Get the old address and port
        old_address = sock.getsockname()
        # Get the old timeout from the handshake
        sock_timeout = sock.gettimeout()
        number_of_packets = len(packets)

        packet = create_packet(sequence_number, acknowledgment_number, 0, receiver_window, packets[0])

        # Take the current time
        sent_time = time.time()
        # Send the packet
        sock.sendto(packet, address)
        last_packet_sent = 1
        print(f"Første sendt: SEQ {sequence_number}, ACK {acknowledgment_number}, {flags}, {receiver_window}")
        old_sent = None

        # Calculating what the next ack should be from server, for validation
        expected_ack = sequence_number + len(packets[0])

        while last_packet_sent < number_of_packets:
            print("\n")
            try:
                # Receive ack from server
                raw_data, address = sock.recvfrom(receiver_window)
                # Decode the header
                sequence_number, acknowledgment_number, flags, receiver_window, data = strip_packet(raw_data)
                # Parse the flags
                syn, ack, fin, rst = parse_flags(flags)

                print(f"Received: SEQ {sequence_number}, ACK {acknowledgment_number}, {flags}, {receiver_window}")

                # If we receive a packet with the correct ack, send the next packet
                if ack and acknowledgment_number == expected_ack:
                    # Set a new timeout for the socket (RTT) * 4
                    sock_timeout = (time.time() - sent_time) * 4
                    sock.settimeout(sock_timeout)
                    # Increase the acknowledgment number
                    expected_ack = acknowledgment_number + len(packets[last_packet_sent])
                    # Save the acknowledgment number
                    holding_ack = acknowledgment_number
                    # Increase the acknowledgment number by 1 to acknowledge the ack packet
                    acknowledgment_number = sequence_number + 1
                    # Set the new sequence number
                    sequence_number = holding_ack

                    # Create the header
                    packet = create_packet(sequence_number, acknowledgment_number, 0, receiver_window,
                                           packets[last_packet_sent])
                    # Send the packet
                    sock.sendto(packet, address)
                    old_sent = packet
                    sent_time = time.time()

                    print(f"Sendt: SEQ {sequence_number}, ACK {acknowledgment_number}, {flags}, {receiver_window}")
                    # Increment the sequence number
                    last_packet_sent += 1

                else:
                    print("Wrong ack number, sending " )
                    # Send the old packet again
                    sock.sendto(old_sent, address)



            # Wait 500 ms before resending the packet
            except TimeoutError as e:
                print(f"Timeout: {e}")
                # Close the socket
                sock.close()
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                # Bind the socket to the old bind
                sock.bind(old_address)
                # Set the socket timeout to 500 ms
                sock.settimeout(sock_timeout)
                # Create the header
                packet = create_packet(sequence_number, acknowledgment_number, 0, receiver_window,
                                       packets[last_packet_sent])

                # Take the current time again
                sent_time = time.time()
                # Resend the last packet
                sock.sendto(packet, address)
                print(f"Sendt: SEQ {sequence_number}, ACK {acknowledgment_number}, {flags}, {receiver_window}")

        # We are done
        return sock
    # Else we are server
    else:
        # Receive the first packet
        packets = []
        previous_acknowledgment_number = acknowledgment_number - 1

        # Start receiving packets
        while True:
            print("\n")
            # Receive ack from client
            raw_data, address = sock.recvfrom(receiver_window)
            # Decode the header
            sequence_number, acknowledgment_number, flags, receiver_window, data = strip_packet(raw_data)
            # Parse the flags
            syn, ack, fin, rst = parse_flags(flags)
            print(f"Received: SEQ {sequence_number}, ACK {acknowledgment_number}, {flags}, {receiver_window}")

            # If the sequence number is equal to the old acknowledgment number, we have received the correct packet
            print(f"SEQ: {sequence_number}, ACK: {acknowledgment_number}, PREV ACK: {previous_acknowledgment_number}")

            if acknowledgment_number == previous_acknowledgment_number + 1:
                previous_acknowledgment_number = acknowledgment_number

                holding_ack = acknowledgment_number

                acknowledgment_number = sequence_number + len(data)
                sequence_number = holding_ack

                # Add the data to the packets list
                packets.append(data)
                # Send the ack
                flags = set_flags(0, 1, 0, 0)
                packet = encode_header(sequence_number, acknowledgment_number, flags, receiver_window)
                sock.sendto(packet, address)
                old_sent_server = packet
                print(f"Sent: SEQ {sequence_number}, ACK {acknowledgment_number}, {flags}, {receiver_window}")
            else:
                print(
                    f"Received duplicate: SEQ {sequence_number}, ACK {acknowledgment_number}, {flags}, {receiver_window}")
                print("Expected ack: " + str(previous_acknowledgment_number + 1))
                flags = set_flags(0, 0, 0, 0)
                sock.sendto(encode_header(sequence_number, acknowledgment_number, flags, receiver_window), address)

            # If the fin flag is set, we are done
            if fin:
                break
        return packets


def GBN(sock, address, sequence_number, acknowledgment_number, flags, receiver_window, packets=None,
        sliding_window=5):
    print("Using GBN")
    # If we are the server, packet_to_send is None
    # If we are the client, we have packets to send (not None)

    # We are the client
    if packets is not None:
        # main_testing("skip_ack")
        # Get the old address and port
        old_address = sock.getsockname()
        # Set the socket timeout to 500 ms
        sock_timeout = 0.5
        # Set the new socket timeout
        sock.settimeout(sock_timeout)

        # Set the last sequence number we received
        last_sequence = sequence_number
        # Set the last acknowledgment number we received
        last_acknowledgement = acknowledgment_number
        # Expected ack
        expected_ack = sequence_number + len(packets[0])

        # Total acks received
        ack_count = 0
        # Total packets sent, used to break out of the loop if we have sent all packets in the interval
        last_packet_sent = 0
        print(f"Antall pakker å sende: {len(packets)}")

        first_seq = sequence_number
        #  ack_count + 1 != len(packets) - 1
        while len(packets) > ack_count:
            print(f"Antall pakker å sende: {len(packets)}")

            # Send the send x packets
            for i in range(ack_count, min(sliding_window + ack_count, len(packets))):
                print(f"Sender pakke {i}")
                if i == ack_count:
                    sequence_number = last_sequence  # Set a new sequence number for the last acked packet
                    acknowledgment_number = last_acknowledgement  # Set a new acknowledgment number for the last acked packet
                else:
                    sequence_number += len(packets[i])  # Set a new sequence number for the next packet

                # Create the header
                packet = create_packet(sequence_number, acknowledgment_number, 0, receiver_window, packets[i])
                # Send the packet
                sock.sendto(packet, address)
                print(f"Sent: SEQ {sequence_number}, ACK {acknowledgment_number}, {flags}, {receiver_window}")
                last_packet_sent = i + 1

            print("Next ack: ", expected_ack)
            print("\n")
            try:
                # Receive the ack
                raw_data, address = sock.recvfrom(receiver_window)
                # Decode the header
                sequence_number, acknowledgment_number, flags, receiver_window, data = strip_packet(raw_data)
                # Parse the flags
                syn, ack, fin, rst = parse_flags(flags)
                print(f"Received: SEQ {sequence_number}, ACK {acknowledgment_number}, {flags}, {receiver_window}")

                # If the ack is correct, update the ack count
                if ack and acknowledgment_number >= expected_ack:
                    # Update the last sequence number and last ack number
                    last_sequence = expected_ack
                    last_acknowledgement = sequence_number
                    ack_count += 1
                    # Update the expected ack
                    expected_ack = expected_ack + len(packets[ack_count])
                    # Update the ack count

                print(f"ack_count: {ack_count}")
            except TimeoutError as e:
                print(f"Timeout: {e}")
                # Close the socket
                sock.close()
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                # Bind the socket to the old bind
                sock.bind(old_address)
                # Set the socket timeout to 500 ms
                sock.settimeout(sock_timeout)

                # Count the acks we have received
                # Send the send x packets
                ack_count = 0
                temp_seq = first_seq
                for i in range(ack_count, len(packets)):
                    if last_sequence == temp_seq:
                        last_sequence = temp_seq + len(packets[ack_count])
                        expected_ack = last_sequence + len(packets[ack_count])
                        sequence_number = last_sequence  # Set a new sequence number for the last acked packet
                        acknowledgment_number = last_acknowledgement  # Set a new acknowledgment number for the last acked packet
                        break
                    temp_seq += len(packets[i])  # Set a new sequence number for the next packet
                    print(f"Ack count: {ack_count}")
                    ack_count += 1
                ack_count += 1

        return sock
    else:
        # Receive the first packet
        packets = []
        first_sequence_number = sequence_number
        next_sequence_number = sequence_number
        prev_sequence_number = sequence_number
        # Start receiving packets
        while True:
            print("\n")
            # Receive ack from client
            raw_data, address = sock.recvfrom(receiver_window)
            # Decode the header
            sequence_number, acknowledgment_number, flags, receiver_window, data = strip_packet(raw_data)
            # Parse the flags
            syn, ack, fin, rst = parse_flags(flags)
            print(
                f"Received: SEQ {sequence_number}, ACK {acknowledgment_number}, {flags}, {receiver_window}, Len {len(data)}", )
            if fin:  # If we have received the last packet exit the loop
                break

            print("Next seq: ", next_sequence_number)
            print(f"Prev : {prev_sequence_number + len(data)}")

            # If the sequence number is the next sequence number, this is true for all packets except the last
            if sequence_number == first_sequence_number or sequence_number == prev_sequence_number + len(data):
                # Update the sequence numbers
                prev_sequence_number = sequence_number
                next_sequence_number = sequence_number + len(data)
                print("Data len " + str(len(data)))
                # Increment the sequence number
                sequence_number = acknowledgment_number + 1
                # Add the data to the packets array
                packets.append(data)
                flags = set_flags(0, 1, 0, 0)
                sock.sendto(encode_header(sequence_number, next_sequence_number, flags, receiver_window), address)
            else:
                print("Duplicate")

        return packets


# Selective-Repeat (SR()): Rather than throwing away packets that arrive in the wrong order, put the packets in
# the correct place in the receive buffer. Combine both GBN and SR to optimise the performance.

def SR(sock, address, sequence_number, acknowledgment_number, flags, receiver_window, packets=None,
       sliding_window=5):
    print("Using SR")
    # If we are the server, packet_to_send is None
    # If we are the client, we have packets to send (not None)

    # We are the client
    if packets is not None:

        # Get the old address and port
        old_address = sock.getsockname()
        # Set the socket timeout to 500 ms
        sock_timeout = 0.5
        # Set the new socket timeout
        sock.settimeout(sock_timeout)

        # Set the last sequence number we received
        sequence_starting_point = sequence_number
        # Set the last acknowledgment number we received
        acknowledgement_starting_point = acknowledgment_number

        # Total acks received
        ack_count = 0

        print(f"Antall pakker å sende: {len(packets)}")

        packets_sent_and_received = [False] * len(packets)
        expected_acks = [""] * len(packets)

        minimum_sequence_number = sequence_number

        starting_point = 0

        total_packets_recevied = 0

        #  ack_count + 1 != len(packets) - 1
        while total_packets_recevied < len(packets):
            print("Acked this interval: ", ack_count)
            ack_count = 0
            # Total packets sent, used to break out of the loop if we have sent all packets in the interval
            packets_sent_in_interval = 0
            sequence_number = sequence_starting_point  # Set a new sequence number for the last acked packet
            acknowledgment_number = acknowledgement_starting_point  # Set a new acknowledgment number for the last acked packet

            print("Starting point: ", starting_point)

            # Send the send x packets
            for i in range(starting_point, min(sliding_window + starting_point, len(packets))):
                # print("\n")
                if packets_sent_and_received[i] is False:
                    print(f"Sending number: {i + 1} av {min(sliding_window + starting_point, len(packets))}")
                    # Create the header
                    packet = create_packet(sequence_number, acknowledgment_number, 0, receiver_window, packets[i])
                    # Send the packet
                    sock.sendto(packet, address)
                    print(f"Sent: SEQ {sequence_number}, ACK {acknowledgment_number}, {flags}, {receiver_window}")
                    packets_sent_in_interval += 1

                sequence_number += len(packets[i])  # Set a new sequence number for the next packet
                expected_acks[i] = sequence_number  # Set the expected ack for the next packet
                if packets_sent_and_received[i] is False:
                    print("Expected ack: ", expected_acks[i])

            # print("\n")
            print("Packets sent in interval: ", packets_sent_in_interval)
            while True:
                try:
                    print("\nSjekker for acks")
                    # Receive the ack
                    raw_data, address = sock.recvfrom(receiver_window)
                    # Decode the header
                    sequence_number, acknowledgment_number, flags, receiver_window, data = strip_packet(raw_data)
                    # Parse the flags
                    syn, ack, fin, rst = parse_flags(flags)
                    print(f"Received: SEQ {sequence_number}, ACK {acknowledgment_number}, {flags}, {receiver_window}")

                    for i in range(starting_point, len(packets)):
                        print(
                            f"Checking packet number: {i + 1} of {min(sliding_window + starting_point, len(packets))}")
                        if expected_acks[i] == "":
                            print("Expected ack is empty, breaking")
                            break
                        # print("Printing i: ", i)
                        # print(f"Sjekker for match {expected_acks[i]}")
                        if ack and acknowledgment_number == expected_acks[i] and packets_sent_and_received[i] is False:
                            print(f"Fant match {expected_acks[i]}")
                            packets_sent_and_received[i] = True
                            # Update the last sequence number and last ack number
                            # Update the ack countk
                            total_packets_recevied += 1
                            ack_count += 1
                            break
                            # Update the expected ack

                        # expected_ack = acknowledgment_number + len(packets[ack_count])

                        # If all the packets we have sent have been acked, we are done
                    print("Packets acked: ", ack_count)
                    if packets_sent_in_interval == ack_count:
                        minimum_sequence_number = sequence_number
                        sequence_starting_point = acknowledgment_number
                        acknowledgement_starting_point = sequence_number
                        starting_point += ack_count
                        print("New starting point: ", starting_point)
                        # Send packets from the last acked packet
                        print("All packets received")
                        break

                except TimeoutError as e:
                    print(f"Timeout: {e}")
                    # Close the socket
                    sock.close()
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    # Bind the socket to the old bind
                    sock.bind(old_address)
                    # Set the socket timeout to 500 ms
                    sock.settimeout(sock_timeout)
                    break

        return sock
    else:
        # Receive the first packet
        packets = []
        packets_acked = []
        buffer = []

        # Start receiving packets
        while True:
            print("\n")
            # Receive ack from client
            raw_data, address = sock.recvfrom(receiver_window)
            # Decode the header
            sequence_number, acknowledgment_number, flags, receiver_window, data = strip_packet(raw_data)
            # Parse the flags
            syn, ack, fin, rst = parse_flags(flags)
            print(
                f"Received: SEQ {sequence_number}, ACK {acknowledgment_number}, {flags}, {receiver_window}, Len {len(data)}", )

            #  If the size of the buffer is the same as the sliding window, we can sort the buffer with the packets
            if len(buffer) == sliding_window or fin:  # If the buffer is full, or we have received the last packet
                buffer.sort(key=lambda x: x[0])  # Sort the buffer by sequence number
                for i in range(len(buffer)):  # Loop through the buffer
                    if len(buffer[i][1]) > 0:  # If the packet is not empty
                        print(buffer[i][0])
                        packets.append(buffer[i][1])  # Add the packet to the packets list
                buffer = []  # Empty the buffer

            if fin:  # If we have received the last packet exit the loop
                break

            # Mark the packet as new
            new_packet = True

            # Check if the packet is a duplicate packet
            for i in range(len(packets_acked)):
                if sequence_number == packets_acked[i]:
                    new_packet = False
                    print("Duplicate packet")
                    break

            # Acknowledge the packet if it's new
            if new_packet:
                packets_acked.append(sequence_number)  # Add the packet to the list of packets that have been acked
                print("New packet")
                buffer.append((sequence_number, data))  # Add the packet to the buffer
                next_acknowledgment_number = sequence_number + len(data)  # Increment the sequence number
                sequence_number = acknowledgment_number + 1  # Increment the sequence number
                flags = set_flags(0, 1, 0, 0)  # Set the flags for ack
                sock.sendto(encode_header(sequence_number, next_acknowledgment_number, flags, receiver_window), address)
                print(f"Sent: SEQ {sequence_number}, ACK {next_acknowledgment_number}, {flags}, {receiver_window}")
            else:
                next_acknowledgment_number = sequence_number + len(data)  # Increment the sequence number
                sequence_number = acknowledgment_number + 1  # Increment the sequence number
                flags = set_flags(0, 1, 0, 0)  # Set the flags for ack
                sock.sendto(encode_header(sequence_number, next_acknowledgment_number, flags, receiver_window), address)
                print(f"Sent: SEQ {sequence_number}, ACK {next_acknowledgment_number}, {flags}, {receiver_window}")


        return packets


def run_client(server_ip, server_port, filename, reliability, mode, window_size):
    try:
        # Set up socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f"Client connecting to {server_port} with IP {server_ip}")

        # Random Initial Sequence Number
        # Keep track of the sequence number, acknowledgment number, flags and receiver window
        sequence_number, acknowledgment_number, flags, receiver_window = random_isn(), 0, 0, 1024
        # sequence_number = 1000

        # Start the three-way handshake, based on https://www.ietf.org/rfc/rfc793.txt page 31
        address = (server_ip, server_port)
        # Flags for syn
        flags = set_flags(1, 0, 0, 0)
        # Create a header with the syn flag set
        packet = encode_header(sequence_number, 0, flags, receiver_window)
        start_time = time.time()
        # Send the packet

        while True:
            sock.sendto(packet, address)
            # Receive the response from the server
            raw_data, address = sock.recvfrom(receiver_window)
            # Parse the header
            sequence_number, acknowledgment_number, flags, receiver_window, data = strip_packet(raw_data)
            print(f"Received: SEQ {sequence_number}, ACK {acknowledgment_number}, {flags}, {receiver_window}")

            # Parse the flags
            syn, ack, fin, rst = parse_flags(flags)
            # Print the flags
            pretty_flags(flags)

            # If we receive a syn and ack from the server we can send a ack to the server
            if syn and ack:
                estimated_rtt = time.time() - start_time
                print(f"Roundtrip time: {estimated_rtt}")
                # Save the acknowledgment number
                acknowledgment_number_prev = acknowledgment_number
                # Increment the sequence number by 1 to acknowledge the syn and ack
                acknowledgment_number = sequence_number + 1
                # Set the sequence number to the acknowledgment number
                sequence_number = acknowledgment_number_prev
                # Flags for ack
                flags = set_flags(0, 1, 0, 0)
                # Create a header with the ack flag set
                packet = encode_header(sequence_number, acknowledgment_number, flags, receiver_window)
                # Send the packet
                sock.sendto(packet, address)
                break
        # Kjør kode eller noe her

        # Get the size of the file
        filesize = os.path.getsize(filename)
        print(f"Filesize: {filesize}")

        # Array to store the packets
        packets_to_send = []

        # The length of the header
        header_length = 12
        # Sending name of file
        # packets_to_send.append(filename.encode())

        # Open the file and send it in chunks of 1024 bytes
        with open(filename, 'rb') as f:
            print(f"Reading from {filename}")
            # Loop until the end of the file
            while True:
                file_raw_data = f.read(receiver_window - header_length)
                # print(file_raw_data.decode())
                # file_raw_data = file_raw_data.decode()
                packets_to_send.append(file_raw_data)
                # print(file_raw_data)  # Print the raw_data we have read from the file
                if not file_raw_data:
                    break

        print(f"Total packets to send {len(packets_to_send)}")
        # reliability = "stop_and_wait"  # For testing
        # reliability = "go_back_n"  # For testing
        # reliability = "selective_repeat"  # For testing

        # Start the timer for the throughput
        start_time = time.time()

        # Send file with mode
        if reliability == "stop_and_wait":
            sock = stop_and_wait(sock, address, sequence_number, acknowledgment_number, flags, receiver_window,
                                 packets_to_send)
        elif reliability == "gbn":
            sock = GBN(sock, address, sequence_number, acknowledgment_number, flags, receiver_window,
                       packets_to_send, window_size)

        elif reliability == "sr":
            sock = SR(sock, address, sequence_number, acknowledgment_number, flags, receiver_window,
                      packets_to_send, window_size)

        # Stop the timer for the throughput
        elapsed_time = time.time() - start_time
        # Calculate the throughput into bits per second
        throughput = (filesize / elapsed_time) * 8
        # Format the throughput to two decimals
        throughput_formatted = "{:.2f}".format(throughput)

        # If the throughput is greater than 1 million, divide by 1 million to get Mbps
        if throughput > 1000000:
            throughput = float(throughput_formatted) / 1000000
            print(f"Throughput: {throughput:.2f} Mbps")
        # If the throughput is greater than 1000, divide by 1000 to get Kbps
        elif throughput > 1000:
            throughput = float(throughput_formatted) / 1000
            print(f"Throughput: {throughput:.2f} Kbps")
        # Else print the throughput in bps
        else:
            print(f"Throughput: {float(throughput_formatted):.2f} bps")

        # SR(sock, address, filename)
        # Start a twoway handshake to close the connection
        # Set the flag to FIN, which is the 3rd element
        packet = encode_header(sequence_number, acknowledgment_number, set_flags(0, 0, 1, 0), receiver_window)
        sock.sendto(packet, address)
        print("FIN sent in the packet header!")

        # Wait for the ACK from the server to finally close everything
        while True:
            raw_data, address = sock.recvfrom(receiver_window)
            sequence_number, acknowledgment_number, flags, receiver_window, data = strip_packet(raw_data)

            # Parse the flags
            syn, ack, fin, rst = parse_flags(flags)

            # If we receive the final ack, we close the connection on the client side
            if fin and ack:
                print("Received ACK for FIN")
                # Close the connection on the client side once we have received an ack
                sock.close()
                break
            else:
                # If we receive a packet with the wrong flags, we send a fin again
                packet = encode_header(sequence_number, acknowledgment_number, set_flags(0, 0, 1, 0), receiver_window)
                sock.sendto(packet, address)

    except KeyboardInterrupt:
        print("Client shutting down")
        exit(0)

    except socket.error as e:
        print(f"Socket error: {e}")
        exit(1)


def run_server(server_ip, server_port, file, reliability, mode, window_size):
    # server_ip, port, client_ip, client_port = "127.0.0.1", 1234, "127.0.0.1", 4321  # For testing
    # server_ip, server_port, client_ip, client_port = "10.0.1.2", 1234, "10.0.0.1", 4321  # For testing

    if mode == "loss":
        run_artificial_testcase("loss")
    if mode == "skip_ack":
        run_artificial_testcase("skip_ack")

    try:
        # Set up socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((server_ip, server_port))
        print(f"Server started on {server_port} with IP {server_ip}")

        # Keep track of the sequence number, acknowledgment number, flags and receiver window
        sequence_number, acknowledgment_number, flags, receiver_window = 0, 0, 0, 64

        # Variable to keep track of the previous sequence_number number
        sequence_number_prev = 0

        # Three-way handshake based on https://www.ietf.org/rfc/rfc793.txt page 31
        while True:
            # Receive the response
            raw_data, address = sock.recvfrom(receiver_window)

            # Parse the header
            sequence_number, acknowledgment_number, flags, receiver_window, data = strip_packet(raw_data)
            # Check if the syn and ack flags are set
            syn, ack, fin, rst = parse_flags(flags)
            print(f"Received: SEQ {sequence_number}, ACK {acknowledgment_number}, {flags}, {receiver_window}")
            pretty_flags(flags)

            # Overwrite the receiver window to 1472 bytes
            receiver_window = 1472

            # Check if the syn flag is set
            if syn:
                # Increment the acknowledgment number by 1 to acknowledge the syn
                acknowledgment_number = sequence_number + 1
                # Random Initial Sequence Number
                sequence_number = random_isn()
                # sequence_number = 0
                # Save the sequence number
                sequence_number_prev = sequence_number
                # Flags for syn and ack
                flags = set_flags(1, 1, 0, 0)
                # Create a header with the syn and ack flags set
                packet = encode_header(sequence_number, acknowledgment_number, flags, receiver_window)
                print(f"Sending: SEQ {sequence_number}, ACK {acknowledgment_number}, {flags}, {receiver_window}")
                pretty_flags(flags)
                # Send the packet
                sock.sendto(packet, address)
            # Check if the ack flag is set and if the acknowledgment number is equal to the previous sequence number + 1
            elif ack and acknowledgment_number == sequence_number_prev + 1:
                print("Connection established")
                break

        # reliability = "stop_and_wait"  # For testing
        # reliability = "go_back_n"  # For testing
        # reliability = "selective_repeat"  # For testing

        packets = []

        start_time = time.time()
        # Send file with mode
        if reliability == "stop_and_wait":
            packets = stop_and_wait(sock, address, sequence_number, acknowledgment_number, flags, receiver_window)

        elif reliability == "gbn":
            packets = GBN(sock, address, sequence_number, acknowledgment_number, flags, receiver_window)
            """packets = OLDGBN(sock, address, sequence_number, acknowledgment_number, flags,
                             receiver_window)  # For testing"""

        elif reliability == "sr":
            packets = SR(sock, address, sequence_number, acknowledgment_number, flags, receiver_window)

        elapsed_time = time.time() - start_time
        filesize = 0
        for packet in packets:
            filesize += len(packet)

        throughput = (filesize / elapsed_time) * 8
        throughput_formatted = "{:.2f}".format(throughput)

        if throughput > 1000000:
            throughput = float(throughput_formatted) / 1000000
            print(f"Throughput: {throughput:.2f} Mbps")
        elif throughput > 1000:
            throughput = float(throughput_formatted) / 1000
            print(f"Throughput: {throughput:.2f} Kbps")
        else:
            print(f"Throughput: {float(throughput_formatted):.2f} bps")

        # SR(sock, address, filename)
        # Kjør kode eller noe her

        close_server_connection(sock, address, sequence_number, receiver_window)

        # basename = str(packets[0].decode())

        file = b""

        for packet in packets:
            file += packet

        """ for packet in range(0, len(packets)):
            file += packets[packet]"""

        save_path = os.path.join(os.getcwd(), "received_files")
        #basename = "nyfil-test.txt"
        basename = "shrek.jpg"
        # basename = f"Fil{time.time()}"

        save_file = open(os.path.join(save_path, basename), 'wb')
        save_file.write(file)
        # save_file.write(file.encode())
        save_file.close()

        subprocess.run(f"chmod 666 {save_path}/{basename}", shell=True)

    except KeyboardInterrupt:
        print("Server shutting down")
        exit(0)

    except socket.error as e:
        print(f"Socket error: {e}")
        exit(1)


# Startet med arparse. Det er fortsatt ikke helt opplagt hva flaggene er, men jeg antar at -m og -r er de samme greiene.
# -m flagget: server og -r flagget: client
def main():
    # Description:
    # Checks is the input is a positive integer, raises an error if it's not.
    # Parameters:
    # integer: holds the integer to check
    # Returns:
    #   Returns the integer if valid, else it will exit the program with an error message
    def check_positive_integer(integer):
        # Default error message message
        error_message = None
        try:
            error_message = "expected an integer but you entered a string"
            integer = int(integer)  # Try to cast to integer
            if 0 >= integer:  # Check if it is a positive number
                error_message = str(integer) + " is not a valid number, must be positive"
                raise ValueError  # Raise error if it is not a positive number
        except ValueError:  # Catch the error if it is not a positive number or not an integer
            print_error(error_message)  # Print using standard error message function
            parser.print_help()
            exit(1)  # Exit the program
        # Return the integer if it is a positive number
        return integer

    # Description:
    #   Checks if an integer from and including 1024 and up to and including 65,535
    # Parameters:
    #   port: holds the port number for server or client
    # Returns:
    #   Returns the port (integer) if valid, else it will exit the program with an error message
    def check_port(port):
        # Default error message message
        error_message = None
        try:
            error_message = "expected an integer but you entered a string"
            port = int(port)
            # Check if port is in range 1024-65535, else raise error_message
            if port < 1024:
                error_message = "Port number is too small, the port must be from 1024 upto 65535"
                raise ValueError
            if 65535 < port:
                error_message = "Port number is too large, the port must be from 1024 upto 65535"
                raise ValueError
        except ValueError:
            print_error(error_message)  # Print using standard error message function
            parser.print_help()
            exit(1)  # Exit the program

        # Return the port number if it is valid
        return port

    # Description:
    #   Checks if an IP address is in dotted decimal notation.
    #   It checks the ranges of the numbers, and if it starts 0.
    # Parameters:
    #   ip: holds the ip address of the server
    # Returns
    #   the ip same ipaddress without leading zeroes, else it will exit the program with an error message
    def check_ipaddress(ip):
        # Default error message message
        error_message = None
        # Split the ip into a list of octets
        ip_split = ip.split(".")
        # Clear the ip string
        ip = ""
        try:
            # Check if we have 4 elements in the list i.e. 3 dots
            if len(ip_split) != 4:
                error_message = f"{ip} is not a valid ip. IPs must be in IPv4 format i.e in dotted decimal notation " \
                                f"X.X.X.X"
                raise ValueError

            # Check if numbers are in range 0-255 and convert i.e. 01 to 1
            for number in ip_split:
                if not number.isdigit():
                    error_message = f"{number} is not a valid number, must be between 0-255"
                    raise ValueError

                if 0 > int(number):
                    error_message = f"{number} is not a valid number, must be positive in the range 0-255"
                    raise ValueError

                # If number is larger
                if 255 < int(number):
                    error_message = f"{number} is not a valid number, must be smaller than 255"
                    raise ValueError

                # Check if its starts with 0
                if int(ip_split[0]) == 0:
                    error_message = f"{ip} ip cannot start with 0"
                    raise ValueError

                # Convert i.e 01 to 1
                ip += f"{int(number)}."
        except ValueError:
            print_error(error_message)  # Print using standard error_message message function
            parser.print_help()
            exit(1)  # Exit the program

        # Remove the last dot
        ip = ip[:-1]
        return ip

    # Description:
    #   Checks if a path exists
    # Parameters:
    #   the path: holds the path
    # Returns:
    #   Returns the path if it exists, else it will exit the program with an error message
    def check_save_path(path):
        # Default error message message
        error_message = None
        try:
            if not os.path.isdir(path):  # Check if the path is a directory
                error_message = f"{path} is not a valid save path"  # Set error_message message
                raise ValueError  # Raise error_message
        except ValueError:
            print_error(error_message)  # Print using standard error_message message function
            parser.print_help()
            exit(1)  # Exit the program
        return path  # Return the path if it exists

    # Description:
    #   Checks if a file exists
    # Parameters:
    #   file: holds the file name
    # Returns:
    #   Returns the file name if it exists, else it will exit the program with an error message
    def check_file(file):
        # Default error message message
        error_message = None
        try:
            if not os.path.isfile(file):  # Check if the file exists
                error_message = f"{file} does not exist"  # Set error_message message
                raise ValueError
        except ValueError:
            print_error(error_message)  # Print using standard error_message message function
            parser.print_help()
            exit(1)  # Exit the program
        return file  # Return the file name if it exists

    # Add description and epilog to the parser, this is for prettier help text
    parser = argparse.ArgumentParser(description="DRTP file transfer application script",
                                     epilog="end of help")

    # Client only arguments
    client_group = parser.add_argument_group('Client')  # Create a group for the client arguments, for the help text
    client_group.add_argument('-c', '--client', action="store_true", help="Run in client mode")
    client_group.add_argument('-r', '--creliability', type=str, choices=["stop_and_wait", "gbn", "sr"],
                              help="Choose reliability mode for client")
    client_group.add_argument('-t', '--mode', type=str, choices=["loss", "skip_ack"], help="Choose your test mode")
    client_group.add_argument('-f', '--file', type=check_file, help="Name of the file")

    # Server only arguments
    server_group = parser.add_argument_group('Server')  # Create a group for the server arguments, for the help text
    server_group.add_argument('-s', '--server', action="store_true", help="Run in server mode")
    server_group.add_argument('-sp', '--server_save_path', type=check_save_path, default=default_server_save_path,
                              help="Path to save items. Default %(""default)s")

    server_group.add_argument('-m', '--sreliability', type=str, choices=["stop_and_wait", "gbn", "sr"],
                              help="Choose reliability mode for server")

    # Common arguments
    parser.add_argument('-i', '--ip', type=check_ipaddress, default=default_ip,
                        help="IP address to connect/bind to, in dotted decimal notation. Default %(default)s")
    parser.add_argument('-p', '--port', type=check_port, default=default_port,
                        help="Port to use, default default %(default)s")
    parser.add_argument('-w', '--window', type=check_positive_integer, default=5,
                        help="Window size, default default %(default)s")

    # Parses the arguments from the user, it calls the check functions to validate the inputs given
    args = parser.parse_args()
    if args.client and args.server:
        print_error("Cannot run as both client and server!")
        sys.exit(1)
    if args.client:
        if args.creliability is None:
            print_error("Client reliability mode is not set!")
            sys.exit(1)
        run_client(args.ip, args.port, args.file, args.creliability, args.mode, args.window)
    elif args.server:
        if args.sreliability is None:
            print_error("Server reliability mode is not set!")
            sys.exit(1)
        run_server(args.ip, args.port, args.server_save_path, args.sreliability, args.mode, args.window)
    else:
        print("Error, you must select server or client mode!")
        parser.print_help()
        sys.exit(1)

    if args.mode is not None:  # If the user has set a test mode i.e. loss or skip_ack remove the artificial test case
        # Remove the artificial test case set by netem
        remove_artificial_testcase()


# Start the main function
if __name__ == "__main__":
    main()
