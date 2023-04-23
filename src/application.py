import argparse
import socket
import threading
import time
import re
import sys
import os
import struct

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
    syn = flags & (1 << 3)  # 1 << 3 = 1000
    ack = flags & (1 << 2)  # 1 << 2 = 0100
    fin = flags & (1 << 1)  # 1 << 1 = 0010
    rst = flags & (1 << 0)  # 1 << 0 = 0001
    return syn, ack, fin, rst


def set_flags(syn, ack, fin, rst):
    flags = 0
    if syn:
        flags |= (1 << 3)
    if ack:
        flags |= (1 << 2)
    if fin:
        flags |= (1 << 1)
    if rst:
        flags |= (1 << 0)
    return flags


# test = set_flags(1, 0, 0, 0)
# print(parse_flags(test))
# print(parse_flags(0b1000))
# print(parse_flags(0b1100))

# Define the structure of the headed
# L = 32 bits, H = 16 bits
# Sequence Number:32 bits, Acknowledgment Number:32, Flags:16 ,Window:16
# From https://docs.python.org/3/library/struct.html
protocol_struct = struct.Struct("!LLHH")


# Description:
#  Function for creating a header with the right format with fixed bit sizes
# Parameters:
#   sequence_number: holds the sequence number
#   acknowledgment_number: holds the acknowledgment number
#   flags: holds the flags
#   window: holds the window
# Returns:
#   Returns the header as a byte string
def create_header(sequence_number, acknowledgment_number, flags, window):
    # Sequence Number:32 bits, Acknowledgment Number:32bits, Flags:16bits, Window:16bits
    return protocol_struct.pack(sequence_number, acknowledgment_number, flags, window)


# Description:
#  Function for parsing a header
# Parameters:
#   header: holds the header
# Returns:
#   Returns the header as a tuple
def parse_header(header):
    return protocol_struct.unpack(header)


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
    data, address = sock.recvfrom(1024)
    filename, filesize = data.decode().split(':')  # Extract filename and filesize
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
        # Receive data
        data, address = sock.recvfrom(1024)
        print(data.decode())
        # Fjern kommentarer for å lagre til fil, dette er kun for testing
        # f.write(data) # Write data to file
        received_bytes += len(data)"""


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
            data, address = sock.recvfrom(1024)
            print(data.decode())


    except KeyboardInterrupt:
        print("Server shutting down")
        exit(0)

    except socket.error as e:
        print(f"Socket error: {e}")
        exit(1)"""


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
                data = f.read(1024)
                print(data.decode())  # Print the data we have read from the file
                if not data:
                    break
                # Send the data we have read
                sock.sendto(data, (ip, port))
    except socket.error as e:
        print(f"Socket error: {e}")
        exit(1)"""


def three_way_handshake_client(sock, address):
    # Create a header with the syn flag set
    packet = create_header(1, 0, set_flags(1, 0, 0, 0), 1)
    # Send the packet
    sock.sendto(packet, address)
    # Receive the response
    data, address = sock.recvfrom(1024)
    # Parse the header
    sequence_number, acknowledgment_number, flags, window = parse_header(data)
    print(f"Received: {sequence_number}, {acknowledgment_number}, {flags}, {window}")
    # Check if the syn and ack flags are set
    syn, ack, fin, rst = parse_flags(flags)
    print(f"Received: {syn}, {ack}, {fin}, {rst}")
    if syn and ack:
        # Create a header with the ack flag set
        packet = create_header(1, 1, set_flags(0, 1, 0, 0), 1)
        # Send the packet
        sock.sendto(packet, address)
        return True


def run_client(port, file, reliability, mode):
    ip, port, serverip, serverport = "127.0.0.1", 4321, "127.0.0.1", 1234  # For testing
    try:
        # Set up socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((ip, port))
        print(f"Client started on {port}")
        # Start the three-way handshake
        if three_way_handshake_client(sock, (serverip, serverport)):
            print("Connection established")

        while True:
            data, address = sock.recvfrom(1024)
            print(data.decode())

            # Send filen eller noe?

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

        while True:
            # Receive the response
            data, address = sock.recvfrom(1024)
            # Parse the header
            sequence_number, acknowledgment_number, flags, window = parse_header(data)
            # Check if the syn and ack flags are set
            syn, ack, fin, rst = parse_flags(flags)
            print(f"Received: {sequence_number}, {acknowledgment_number}, {flags}, {window}")
            print(f"Received: {syn}, {ack}, {fin}, {rst}")
            if syn:
                # Create a header with the syn flag set
                packet = create_header(1, 1, set_flags(1, 1, 0, 0), 1)
                sock.sendto(packet, address)
                print("Sent syn and ack")
            elif ack:
                print("Connection established")
                break
        # Kjør kode eller noe
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

    # Server only arguments
    server_group = parser.add_argument_group('Server')  # Create a group for the server arguments, for the help text
    server_group.add_argument('-s', '--server', action="store_true", help="Run in server mode")
    server_group.add_argument('-b', '--bind', type=check_ipaddress, default=default_ip,
                              help="IP address to connect/bind to, in dotted decimal notation. Default %(default)s")
    server_group.add_argument('-sp', '--server_save_path', type=check_save_path, default=default_server_save_path,
                              help="Path to save items. Default %(""default)s")
    # DRTP arguments
    drtp_group = parser.add_argument_group('Protocol')  # Create a group for the DRTP arguments, for the help text
    drtp_group.add_argument('-r', '--reliability', type=str, choices=["stop_and_wait", "gbn", "sr"],
                            help="Choose Reliability mode")
    drtp_group.add_argument('-t', '--mode', type=str, choices=["loss", "skipack"], help="Choose your test mode")

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
        run_client(args.port, args.file, args.reliability, args.mode)
    elif args.server:
        run_server(args.port, args.file, args.reliability, args.mode)
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
