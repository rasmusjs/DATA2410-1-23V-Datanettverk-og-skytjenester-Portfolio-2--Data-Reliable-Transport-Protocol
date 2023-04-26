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

# Default values
formatting_line = "-" * 45  # Formatting line = -----------------------------
default_server_save_path = "server_files"  # Path to the folder where received files are stored
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


# test = set_flags(1, 0, 0, 0)
# print(parse_flags(test))
# print(parse_flags(0b1000))
# print(parse_flags(0b1100))

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
    return sequence_number, acknowledgment_number, flags, receiver_window, data.decode()


def create_packet(sequence_number, acknowledgment_number, flags, window, data):
    header = encode_header(sequence_number, acknowledgment_number, flags, window)
    return header + data.encode()


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


# Description:
#   Starts the server
# Parameters:
#   ip: holds the ip address
#   port: holds the port
#   save_path: holds the save path
# Returns:
#   None
def start_server(ip, port, save_path):
    pass
    """print("Starting server")
    try:
        # Set up socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((ip, port))
        print(f"Server started on {ip}:{port}")
        while True:
            # threading.Thread(target=handle_client, args=(sock,)).start()
            # server_handle_client(sock, save_path)
            raw_data, address = sock.recvfrom(1024)
            print(raw_data.decode())


    except KeyboardInterrupt:
        print("Server shutting down")
        exit(0)

    except socket.error as e:
        print(f"Socket error: {e}")
        exit(1)"""


def read_file(filename):
    return open(filename, 'rb')


# Description:
#   Starts the client
# Parameters:
#   ip: holds the ip address
#   port: holds the port
#   filename: holds the filename
# Returns:
#   None,
def start_client(ip, port, filename):
    pass
    """print("Starting client")
    try:
        # Create a socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Get the size of the file
        filesize = os.path.getsize(filename)

        # Send file name and size (this should be the header)
        sock.sendto(f"{filename}:{filesize}".encode(), (ip, port))
        # Open the file and send it in chunks of 1024 bytes
        with open(filename, 'rb') as f:
            # Loop until the end of the file
            while True:
                raw_data = f.read(1024)
                print(raw_data.decode())  # Print the raw_data we have read from the file
                if not raw_data:
                    break
                # Send the raw_data we have read
                sock.sendto(raw_data, (ip, port))
    except socket.error as e:
        print(f"Socket error: {e}")
        exit(1)"""


# Description:
#   Create a random initial sequence number for the three-way handshake
# Parameters:
#   None
# Returns:
#   Returns a random initial sequence number as an integer
def random_isn():
    return random.randint(0, 2 ** 32 - 1)


def stop_and_wait(sock, address, sequence_acknowledgment_prev, packet_to_send=None):
    # If we are the server, packet_to_send is None
    # If we are the client, we have packets to send (not None)

    # We are the client
    if packet_to_send is not None:
        number_of_packets = len(packet_to_send)
        last_packet_number = 1
        acknowledgment_number_prev = sequence_acknowledgment_prev
        # Set the socket timeout to 500 ms
        sock.settimeout(5)

        while True:
            try:
                # Receive ack from server
                raw_data, address = sock.recvfrom(64)
                # Decode the header
                sequence_number, acknowledgment_number, flags, receiver_window, data = strip_packet(raw_data)
                # Parse the flags
                syn, ack, fin, rst = parse_flags(flags)
                if ack and acknowledgment_number > sequence_acknowledgment_prev:
                    # Fix the sequence number and acknowledgment number here

                    # Save the acknowledgment number
                    acknowledgment_number_prev = acknowledgment_number
                    # Increment the sequence number by 1 to acknowledge the syn and ack
                    acknowledgment_number = sequence_number + len(packet_to_send[last_packet_number])
                    # Set the sequence number to the acknowledgment number
                    sequence_number = acknowledgment_number_prev

                    # Create the header
                    packet = create_packet(sequence_number, acknowledgment_number, 0, receiver_window,
                                           packet_to_send[last_packet_number])

                    # Send the packet
                    sock.sendto(packet, address)

                    # Increment the sequence number
                    last_packet_number += 1
                    # If the sequence number is equal to the number of packets, we are done
                    if last_packet_number == number_of_packets:
                        break

            # Wait 500 ms
            except sock.timeout:
                # Resend the last packet
                sock.sendto(packet_to_send[last_packet_number - 1], address)

        # Close the socket


    # Else we are server
    else:
        # Receive the first packet
        packet_to_send = []
        sequence_number_prev = sequence_acknowledgment_prev
        while True:
            # Receive ack from client
            raw_data, address = sock.recvfrom(64)
            # Decode the header
            sequence_number, acknowledgment_number, flags, receiver_window, data = strip_packet(raw_data)
            # Parse the flags
            syn, ack, fin, rst = parse_flags(flags)

            if sequence_number_prev < acknowledgment_number:
                print("Received packet")

                # Increment the acknowledgment number by 1 to acknowledge the syn
                acknowledgment_number = sequence_number + len(data)

                # Save the sequence number
                sequence_number_prev = sequence_number

                packet_to_send.append(data)
                # Send the ack
                flags = set_flags(0, 1, 0, 0)
                sock.sendto(encode_header(sequence_number, acknowledgment_number, flags, receiver_window), address)
                print("Sent ack")

                # If the ack is the last packet, we are done
                if fin:
                    break

        return packet_to_send

    # Forklaring:
    # Send første pakke med sequence number 0 og ACK number 0
    # Vent på ACK eller NAK i 500ms med socket.settimeout(0.5)
    # Hvis ACK, send neste pakke
    # Hvis NAK, send samme pakke på nytt


def GBN(sock, address, packet_to_send=False):
    pass
    # Go-Back-N (GBN()): sender implements the Go-Back-N strategy using a fixed window size of 5 packets to transfer
    # raw_data. The sequence numbers represent packets, i.e. packet 1 is numbered 1, packet 2 is numbered 2 and so on.
    # If no ACK packet is received within a given timeout (choose a default value: 500ms, use socket.settimeout()
    # function), all packets that have not previously been acknowledged are assumed to be lost, and they are
    # retransmitted. A receiver passes on raw_data in order, and if packets arrive at the receiver in the wrong order,
    # this indicates packet loss or reordering in the network. The DRTP receiver should in such cases not acknowledge
    #  anything and may discard these packets.


def SR(sock, address, packet_to_send=False):
    pass
    # Selective-Repeat (SR()): Rather than throwing away packets that arrive in the wrong order, put the packets in
    # the correct place in the receive buffer. Combine both GBN and SR to optimise the performance.


def run_client(port, filename, reliability, mode):
    ip, port, serverip, serverport = "127.0.0.1", 4321, "127.0.0.1", 1234  # For testing
    filename = "test.txt"
    try:
        # Set up socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((ip, port))
        print(f"Client started on {port}")
        # Random Initial Sequence Number
        # Keep track of the sequence number, acknowledgment number, flags and receiver window
        sequence_number, acknowledgment_number, flags, receiver_window = random_isn(), 0, 0, 1024

        # Keep track of the previous acknowledgment number
        acknowledgment_number_prev = 0

        # Start the three-way handshake, based on https://www.ietf.org/rfc/rfc793.txt page 31

        address = (serverip, serverport)

        # Flags for syn
        flags = set_flags(1, 0, 0, 0)

        # Create a header with the syn flag set
        packet = encode_header(sequence_number, 0, flags, receiver_window)
        # Send the packet
        sock.sendto(packet, address)

        while True:
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

        # Calculate the number of packets to send
        packet_count = math.ceil(filesize / receiver_window)

        packets_to_send = []

        header_length = 12
        # Open the file and send it in chunks of 1024 bytes
        with open(filename, 'rb') as f:
            print(f"Reading from {filename}")
            # Loop until the end of the file
            while True:
                file_raw_data = f.read(receiver_window - header_length)
                file_raw_data = file_raw_data.decode()
                packets_to_send.append(file_raw_data)
                print(file_raw_data)  # Print the raw_data we have read from the file
                if not file_raw_data:
                    break

        # Create the packet
        packet = create_packet(sequence_number + len(packets_to_send[0]), acknowledgment_number, 0, receiver_window,
                               packets_to_send[0])
        # Send the packet
        sock.sendto(packet, address)

        reliability = "stop_and_wait"  # For testing

        # Send file with mode
        if reliability == "stop_and_wait":
            stop_and_wait(sock, address, acknowledgment_number, packets_to_send)

        elif reliability == "go_back_n":
            pass
            # GBN(sock, address, filename)

        elif reliability == "selective_repeat":
            pass
            # SR(sock, address, filename)

        # Start a twoway handshake to close the connection
        # Set the flag to FIN, which is the 3rd element
        flags = set_flags(0, 0, 1, 0)
        packet = encode_header(sequence_number, acknowledgment_number, flags, receiver_window)
        sock.sendto(packet, address)
        print("FIN sent in the packet header!")

        # Wait for the ACK from the server to finally close everything
        while True:
            raw_data, address = sock.recvfrom(receiver_window)
            sequence_number, acknowledgment_number, flags, receiver_window, data = strip_packet(raw_data)

            # Parse the flags
            syn, ack, fin, rst = parse_flags(flags)

            # If we receive the final ack, we close the connection on the client side
            if ack:
                print("Received ACK for FIN")
                # Close the connection on the client side once we have received an ack
                sock.close()
                break


        while True:
            packet = encode_header(sequence_number, acknowledgment_number, flags, receiver_window)
            data = packet + "Hello World".encode()
            sock.sendto(data, address)
            data, address = sock.recvfrom(receiver_window)
            print(data.decode())

    except KeyboardInterrupt:
        print("Client shutting down")
        exit(0)

    except socket.error as e:
        print(f"Socket error: {e}")
        exit(1)


def run_server(port, file, reliability, mode):
    ip, port, clientip, clientport = "127.0.0.1", 1234, "127.0.0.1", 4321  # For testing

    try:
        # Set up socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((ip, port))
        print(f"Server started on {port}")

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

            # Overwrite the receiver window to 64
            receiver_window = 64

            # Check if the syn flag is set
            if syn:
                # Increment the acknowledgment number by 1 to acknowledge the syn
                acknowledgment_number = sequence_number + 1
                # Random Initial Sequence Number
                sequence_number = random_isn()
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

        reliability = "stop_and_wait"  # For testing

        # Send file with mode
        if reliability == "stop_and_wait":
            stop_and_wait(sock, address, acknowledgment_number)

        elif reliability == "go_back_n":
            pass
            # GBN(sock, address, filename)

        elif reliability == "selective_repeat":
            pass
            # SR(sock, address, filename)
        # Kjør kode eller noe her

        while True:  # <---
            raw_data, address = sock.recvfrom(receiver_window)
            sequence_number, acknowledgment_number, flags, receiver_window, data = strip_packet(raw_data)

            # Parse the flags
            syn, ack, fin, rst = parse_flags(flags)

            # If we receive the FIN from the client, send an ACK
            if fin:
                print("Received FIN from the client")
                acknowledgment_number = sequence_number + 1
                flags = set_flags(1, 1, 0, 0)  # Set the ACK flag
                packet = encode_header(sequence_number, acknowledgment_number, flags, receiver_window)
                sock.sendto(packet, address)
                print("Sent ACK for FIN")
                # Close the connection on the 
                sock.close()
                break  # <---

        """while True:
            raw_data, address = sock.recvfrom(receiver_window)
            # Parse the header
            sequence_number, acknowledgment_number, flags, receiver_window, data = strip_packet(raw_data)
            print(f"Received: SEQ {sequence_number}, ACK {acknowledgment_number}, {flags}, {receiver_window}")
            print(f"Received raw_data: {data}")"""

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
    client_group.add_argument('-a', '--serverip', type=check_ipaddress, default=default_ip,
                              help="Bind the server to a specific ip address, in dotted decimal notation. Default %("
                                   "default)s")
    client_group.add_argument('-r', '--creliability', type=str, choices=["stop_and_wait", "gbn", "sr"],
                              help="Choose reliability mode for client")
    client_group.add_argument('-t', '--mode', type=str, choices=["loss", "skipack"], help="Choose your test mode")

    # Server only arguments
    server_group = parser.add_argument_group('Server')  # Create a group for the server arguments, for the help text
    server_group.add_argument('-s', '--server', action="store_true", help="Run in server mode")
    server_group.add_argument('-b', '--bind', type=check_ipaddress, default=default_ip,
                              help="IP address to connect/bind to, in dotted decimal notation. Default %(default)s")
    server_group.add_argument('-sp', '--server_save_path', type=check_save_path, default=default_server_save_path,
                              help="Path to save items. Default %(""default)s")

    server_group.add_argument('-m', '--sreliability', type=str, choices=["stop_and_wait", "gbn", "sr"],
                              help="Choose reliability mode for server")

    # Common arguments
    parser.add_argument('-p', '--port', type=check_port, default=default_port,
                        help="Port to use, default default %(default)s")
    parser.add_argument('-f', '--file', type=check_file, help="Name of the file")

    # Parses the arguments from the user, it calls the check functions to validate the inputs given
    args = parser.parse_args()
    if args.client and args.server:
        print_error("Cannot run as both client and server!")
        sys.exit(1)
    if args.client:
        run_client(args.port, args.file, args.creliability, args.mode)
    elif args.server:
        run_server(args.port, args.file, args.sreliability, args.mode)
    else:
        print("Error, you must select server or client mode!")
        parser.print_help()
        sys.exit(1)

    # Dette er den gamle main funksjonen, som ikke fungerer med argparse enda
    # if args.server:
    #    start_server(args.server_ip, args.port, args.server_save_path)
    #    # End of server mode
    #
    #   if args.client:
    #    start_client(args.client_ip, args.port, args.filename)
    #    # End of client mode


# Start the main function
if __name__ == "__main__":
    main()
