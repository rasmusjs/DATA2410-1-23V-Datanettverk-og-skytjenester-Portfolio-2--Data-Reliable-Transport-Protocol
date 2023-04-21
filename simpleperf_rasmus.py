import argparse
import socket
import threading
import time
import re
import sys

# Global variables
KILOBYTE = 1000  # Size of one kilobyte, used for calculating the rate and the size of the packages
transmissions = []  # List that holds the transmissions in progress
finished_transmissions = []  # List that holds the finished transmissions
interval_elapsed_time = 0.0  # Total time for all transmissions
summary_print_index = 0  # Index of the last printed transmission
summary_header_print = True  # Boolean to check if the summary header has been printed
formatting_line = "-" * 45  # Formatting line = -----------------------------
FORMAT_RATE_UNIT = ""  # Format for the rate unit i MB/s or KB/s


# Description:
#   Class for holding the data for each transmission for server and clients
# Arguments:
#   ip_port_pair: holds the ip address of the server and the port number used, i.e. 10.0.0.2:5000
#   elapsed_time: holds the time it took to send the data
#   interval_bytes: holds the data sent in this interval in bytes, it is used to calculate the rate in given interval
#   total_bytes: holds the data sent in total.
# Returns:
#   itself, it is used to create a new object of the transmission instead of using a tuple or printing directly
class Transmission:
    def __init__(self, ip_port_pair, elapsed_time, interval_bytes, total_bytes):
        self.ip_port_pair = ip_port_pair
        self.elapsed_time = elapsed_time
        self.interval_sent_data = interval_bytes
        self.total_bytes = total_bytes


# Description:
#   Function for printing error messages, to standard error output with formatting
# Global variables:
#   error_message: string with the error message to print
# Returns:
#   nothing, it prints the error message with red color and "Error" to standard error output
def print_error(error_message):
    print(f"\033[1;31;1mError: \n\t{error_message}\n\033[0m", file=sys.stderr)


# Description:
#   Prints a formatting line and which port a server is listening on.
# Parameters:
#   listening_port: holds the port number the server is listening from input parameters set by the user
# Returns:
#   nothing, it prints the formatting line and the port number
def print_server_listening_port(listening_port):
    print(formatting_line)
    print(f"A simpleperf server is listening on port {listening_port}")
    print(formatting_line)


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
            error_message = f"{ip} is not a valid ip. IPs must be in IPv4 format i.e in dotted decimal notation X.X.X.X"
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
#   checks if number of bytes to send is in the correct format using regex
#   It checks if the string starts with a number and ends with B, KB or MB
# Parameters:
#   number of bytes (nbytes) holds the number of bytes to send with the unit i.e. 1B, 1KB, 1MB
# Returns:
#   a string if its valid, else it will exit the program with an error message
def check_nbytes(nbytes):
    # Check if string starts with number and ends with B, KB or MB.
    check = re.compile(r"^[0-9]+(B|KB|MB)$")  # Format required i.e. 1B, 1KB, 1MB
    try:
        # Check if the string is valid and raise an error if it is not
        if not check.match(nbytes):
            raise ValueError
    except ValueError:
        print_error(f"Invalid numbers to send must end with B, KB or MB. {nbytes} is not recognized")
        parser.print_help()
        exit(1)  # Exit the program
    # Return the string if it is valid
    return nbytes


# Add description and epilog to the parser, this is for prettier help text
parser = argparse.ArgumentParser(description="Simpleperf, a simple iPerf clone for testing network performance.",
                                 epilog="end of help")

# This is the default values, these are set outside. This is so they can be used in the client or server specific arguments
default_ip = "127.0.0.1"
default_time = 25
default_parallel = 1
default_port = 8088
default_print_format = "MB"

# Client only arguments
client_group = parser.add_argument_group('client')  # Create a group for the client arguments, for the help text
client_group.add_argument('-c', '--client', action="store_true", help="Start in client mode")
client_group.add_argument('-I', '--serverip', type=check_ipaddress, default=default_ip,
                          help="Server ip address to connect to, in dotted decimal notation. Default %(default)s")
client_group.add_argument('-t', '--time', type=check_positive_integer, default=default_time,
                          help="Time to run the client in seconds, it will try to send as many packets as possible in the given time. Default %(default)s seconds")
client_group.add_argument('-i', '--interval', type=check_positive_integer,
                          help="Print statistics every x seconds. If not set it will print when the client is finished.")
client_group.add_argument('-P', '--parallel', type=int, default=default_parallel, choices=range(1, 6),
                          help="Number of parallel clients. Default is  %(default)s client")
client_group.add_argument('-n', '--num', type=check_nbytes,
                          help="Number of bytes to send i.e 10MB. Valid units B, MB or KB.")

# Server only arguments
server_group = parser.add_argument_group('server')  # Create a group for the server arguments, for the help text
server_group.add_argument('-s', '--server', action="store_true", help="Start in server mode")
server_group.add_argument('-b', '--bind', type=check_ipaddress, default=default_ip,
                          help="Bind the server to a specific ip address, in dotted decimal notation. Default %(default)s")

# Common arguments
parser.add_argument('-p', '--port', type=check_port, default=default_port,
                    help="Port to use, default default %(default)s")
parser.add_argument('-f', '--format', type=str, default=default_print_format, choices=("B", "KB", "MB"),
                    help="Format to print the data in, default %(default)s")

# Parses the arguments from the user, it calls the check functions to validate the inputs given
args = parser.parse_args()


# Description:
#   This function will print the statistics of a transmission of the client or server
# Parameters:
#   server_mode: boolean, if server_mode is set it will print a different summary with different headers and intervals
# Global variables:
#   interval_elapsed_time: hold the interval time of the last summary
#   transmissions: holds the transmissions. With server mode this is the finished transmissions, else it's the transmissions in an interval
#   finished_transmissions: holds the finished transmissions, if the interval_byte is 0 the transmission is finished and will be added to this list
#   summary_print_index: holds the index of the summary, this is used to print the ID of the summary
#   FORMAT_RATE_UNIT: holds the unit to print the rate in, this is set in the main function
# Returns:
#   nothing, it will print the summary
def general_statistics(server_mode=False):
    # Set the total time to 0, this will be used to calculate the interval
    total_time = 0.0

    global interval_elapsed_time
    global transmissions
    global finished_transmissions
    global summary_print_index
    global FORMAT_RATE_UNIT

    if server_mode:
        print(f"\n{'ID':<15s}{'Interval':^15s}{'Received':^15s}{'Rate':^15s}")
    else:
        global summary_header_print
        if summary_header_print is True:
            # Print the header of the summary table only once if we are the client
            print(f"\n{'ID':<15s}{'Interval':^15s}{'Transfer':^15s}{'Bandwidth':^15s}")
            summary_header_print = False

    if len(transmissions) == 0:
        return

    # Calculate the packet size in bytes
    FORMAT_BIT = 0
    FORMAT_RATE_UNIT = ""

    # Convert the data_total bytes to the desired format i.e B, KB or MB from --format
    if args.format == "B":
        FORMAT_BIT = 1
        FORMAT_RATE_UNIT = "bps"
    elif args.format == "KB":
        FORMAT_BIT = 1 / KILOBYTE
        FORMAT_RATE_UNIT = "Kbps"
    elif args.format == "MB":
        FORMAT_BIT = 1 / (KILOBYTE * KILOBYTE)
        FORMAT_RATE_UNIT = "Mbps"

    # Loop through all the transmissions from the summary_print_index
    for j in range(summary_print_index, len(transmissions)):
        transmission = transmissions[j]
        (ip_port_pair, elapsed_time, interval_sent_data,
         total_sent) = transmission.ip_port_pair, transmission.elapsed_time, transmission.interval_sent_data, transmission.total_bytes

        if summary_print_index == j:
            if interval_sent_data != 0 or args.interval is None or server_mode:
                # If the client is using the interval flag, we need to calculate the interval time
                if args.interval is not None:
                    total_time = interval_elapsed_time
                    elapsed_time = interval_elapsed_time + args.interval
                    # Convert the received bytes to the desired format i.e B, KB or MB from --format
                    received = interval_sent_data * FORMAT_BIT
                else:
                    received = total_sent * FORMAT_BIT

                # Format the values to 2 decimal places and add the units
                f_interval = f"{round(total_time, 2)} - {round(elapsed_time, 2)}"  # i.e  0.00 - 10.00
                f_received = f"{round(received, 2)} {args.format}"  # i.e  16.00 MB
                # If the interval is set elapsed_time will be the interval time, else it will be the total time
                if args.interval is not None:
                    elapsed_time = args.interval

                f_rate = f"{round((received / elapsed_time) * 8, 2)} {FORMAT_RATE_UNIT}"  # i.e  128.00 Mbps

                # Print the summary of the transmission
                print(f"{ip_port_pair:^15s}{f_interval:^15s}{f_received:^15s}{f_rate:^15s}")

            # Add the transmission to the finished_transmissions list if it's the last transmission
            if interval_sent_data == 0 or server_mode:
                # Convert the total bytes to the desired format i.e B, KB or MB from --format
                total_sent = round(total_sent * FORMAT_BIT, 2)
                finished_transmissions.append(Transmission(ip_port_pair, elapsed_time, interval_sent_data, total_sent))

        # Increment the summary_print_index, this is used to print the summary only once
        summary_print_index += 1

    if args.interval is not None:
        interval_elapsed_time += args.interval

    # if server:
    #    print_total()


# Description:
#   This function prints the total summary of the client or server
# Global variables:
#   finished_transmissions: holds the finished transmissions, if the interval_byte is 0 the transmission is finished and will be added to this list
#   FORMAT_RATE_UNIT: holds the unit to print the rate in, this is set by general_statistics
# Returns:
#   nothing, it will print the total summary of the client or server
def print_total():
    global finished_transmissions
    global FORMAT_RATE_UNIT
    # Wait for the other parallel clients to finish, only applicable if a client is using the -P flag
    if len(finished_transmissions) != args.parallel and args.parallel != 1:
        time.sleep(0.1)

    print(formatting_line)
    for transmission in finished_transmissions:
        (ip_port_pair, elapsed_time, interval_sent_data,
         total_sent) = transmission.ip_port_pair, transmission.elapsed_time, transmission.interval_sent_data, transmission.total_bytes
        # Format the values to 2 decimal places and add the units
        f_interval = f"0 - {round(elapsed_time, 2)}"  # i.e  0.00 - 10.00
        f_received = f"{round(total_sent, 2)} {args.format}"  # i.e  16.00 MB
        f_rate = f"{round((total_sent / elapsed_time) * 8, 2)} {FORMAT_RATE_UNIT}"  # i.e  128.00 Mbps
        print(f"Total {ip_port_pair:^15s}{f_interval:^15s}{f_received:^15s}{f_rate:^15s}")
    finished_transmissions.clear()


# Description:
#   This function is used to handle the client when it joins the server.
#   It will also print the summary and add the transmission to the global variable transmissions
# Parameters:
#   c_socket: the socket of the client
#   c_addr: the address of the client (ip, port)
# Global variables:
#   transmissions: holds the transmissions of the client on the server side
# Returns:
#   nothing, it will handle the client and print the summary
def server_handle_client(c_socket, c_addr):
    # Create the ip:port pair
    ip_port_pair = f"{c_addr[0]}:{c_addr[1]}"
    print_server_listening_port(args.port)
    print(f"\nA simpleperf client with {ip_port_pair} is connected with {args.bind}:{args.port}")

    # Get the global variable for the server_transmissions
    global transmissions
    # Current time
    start_time = time.time()
    # Size of the packet
    total_received = 0

    while True:
        try:
            # Get the request
            packet = c_socket.recv(KILOBYTE)
            # Add the size of the packet
            total_received += len(packet)
            # Remove the escape character
            packet = packet.strip(b'\x10')
            # Decode the packet
            packet = packet.decode()

            # Check if the client wants to EXIT
            if packet == "BYE":
                # Update the elapsed time one last time
                elapsed_time = time.time()
                total_received -= len("BYE")
                # Send the response
                c_socket.send("ACK:BYE".encode())
                # Close the socket after sending the response
                c_socket.close()
                # Save the results of the transmission
                transmissions.append(
                    Transmission(ip_port_pair, elapsed_time - start_time, total_received, total_received))
                break
        except ConnectionResetError:
            elapsed_time = time.time()
            print_error(f"Connection to {ip_port_pair} has been lost")
            transmissions.append(Transmission(ip_port_pair, elapsed_time - start_time, total_received, total_received))
            break
    general_statistics(True)


# Description:
#   This function is used to start the server.
#   When a client connects, it will create a new thread to handle the client i.e. server_handle_client.
# Parameters:
#   the function takes no parameters in its signature, but it uses the parameters from argparse
#   ip: the ip to bind the socket to
#   port: the port to bind the socket to
#   format: the format to print the data in i.e B, KB or MB
# Returns:
#   nothing, it will start an instance the server
def start_server():
    # Try to create the socket
    try:
        # Create socket
        s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Try to bind to the ip and port and accept connections

        # Bind the socket to the host and port
        s_socket.bind((args.bind, int(args.port)))
        print_server_listening_port(args.port)
        s_socket.settimeout(60 * 10)  # Set the timeout to 10 minutes
    except socket.error:
        print_error("Failed to bind socket, maybe is the port and ip is taken already?")
        exit(1)

    # Start listening for connections
    s_socket.listen()

    while True:
        try:
            # Accept connections
            c_socket, c_addr = s_socket.accept()
            # Create a new thread for each client to handle the connection
            threading.Thread(target=server_handle_client, args=(c_socket, c_addr)).start()
        except socket.timeout:
            # Close the socket
            s_socket.close()
            print(f"\nServer shutting down, no clients connected after {s_socket.gettimeout() / 60} minutes...")
            exit(0)
        except KeyboardInterrupt:
            # Close the socket
            s_socket.close()
            print("\nServer shutting down...")
            exit(0)


# Description:
#   This function is used to start a single instance of the client, the client will try to connect to a server using
#   TCP sockets with the given port and ip
# Parameters:
#   the function takes no parameters in its signature, but it uses the parameters from argparse
#   serverip: the ip of the server to connect to
#   port: the port to use for initiating the connection
#   time: the time to run the client for
#   num: the number of bytes to send
# Global variables:
#  transmissions: holds the transmissions. With server mode this is the finished transmissions, else it's the transmissions in an interval
# Returns:
#   nothing, it will start a single instance a client
def client_start_client():
    try:
        # Use the global variables
        global transmissions

        # Total sent keeps track of how many bytes we have sent in total
        total_sent = 0
        # Keep track of how many bytes we have sent in this interval
        interval_sent_data = 0

        # This variable is used to calculate the interval time for saving the transmission
        save_interval = 0

        # Create a new socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the host and port
        sock.connect((args.serverip, args.port))

        # Get the ip and port of the client and format it to ip:port
        ip_port_pair = f"{sock.getsockname()[0]}:{sock.getsockname()[1]}"

        # Print the client ip and port if we are using multiple clients
        if args.parallel == 1:
            print(f"Client connected to server {args.serverip}, port {args.port}")
        else:
            print(f"Client {ip_port_pair} connected with server {args.serverip}, port {args.port}")

        # If the user has specified an interval, set the next interval to the current time + the interval time.
        # -0.05 to make sure we don't miss the interval for saving the results for the transmission
        SAVE_OFFSET = -0.05
        if args.interval is not None:
            save_interval = time.time() + int(args.interval) + SAVE_OFFSET

        # If the number of bytes is specified, send the data in chunks of 1KB until all the bytes is sent
        if args.num is not None:
            # Size of the data to send in bytes
            packet_size = 0

            # Get the packet size in bytes, and remove the units from the number
            if args.num.endswith("MB"):
                packet_size = int(args.num[:-2]) * KILOBYTE * KILOBYTE
            elif args.num.endswith("KB"):
                packet_size = int(args.num[:-2]) * KILOBYTE
            elif args.num.endswith("B"):
                packet_size = int(args.num[:-1])

            # Fill a buffer with the number of bytes specified
            dump = b'\x10' * packet_size

            # Set the start time to the current time
            start_time = time.time()
            # Loop until we have sent all the bytes
            while total_sent < packet_size:
                # Get the number of bytes to send, either one KILOBYTE or the remaining bytes
                bytes_to_send = min(KILOBYTE, packet_size - total_sent)
                # Send in chunks of a KILOBYTE or the remaining bytes
                sock.send(dump[:bytes_to_send])
                # Update the total sent
                total_sent += bytes_to_send
                # Update the total sent
                interval_sent_data += KILOBYTE
                # Save the transmission every interval, if set
                if time.time() > save_interval != 0:
                    # Update the elapsed time
                    elapsed_time = time.time() - start_time
                    save_interval = time.time() + int(args.interval) + SAVE_OFFSET
                    transmissions.append(Transmission(ip_port_pair, elapsed_time, interval_sent_data, total_sent))
                    interval_sent_data = 0
        # Else we send data for a specified time given by the time flag, we
        else:
            # Set the runtime
            runtime = time.time() + int(args.time)
            # Set the start time to the current time
            start_time = time.time()
            while time.time() <= runtime:
                # Send the data in chunks of KILOBYTE
                sock.send(b'\x10' * KILOBYTE)
                total_sent += KILOBYTE
                # Update the total sent
                interval_sent_data += KILOBYTE
                # Save the transmission every interval, if set
                if time.time() > save_interval != 0:
                    # Update the elapsed time
                    elapsed_time = time.time() - start_time
                    save_interval = time.time() + int(args.interval) + SAVE_OFFSET
                    transmissions.append(Transmission(ip_port_pair, elapsed_time, interval_sent_data, total_sent))
                    interval_sent_data = 0

        # Graceful close of connection by sending BYE
        sock.send("BYE".encode())

        # Then wait for the server to close the connection by sending ACK:BYE
        response = sock.recv(KILOBYTE).decode()
        if response == "ACK:BYE":
            # Update the elapsed time one last time
            elapsed_time = time.time() - start_time
            # Close the socket
            sock.close()
            # Update the transmission, and set the interval_bytes to 0 since we are done sending data
            transmissions.append(Transmission(ip_port_pair, elapsed_time, 0, total_sent))

    except ConnectionRefusedError:
        print_error("Connection refused. Please check the host and port, and try again.")
        exit(1)


# Description:
#   This function is used to print the summary of the client every x seconds while we have clients running
# Parameters:
#  client_treads: the list of threads that are started running
# Arguments:
#   none
# Returns:
#   nothing, but prints the summary of all the clients running
def interval_timer(client_treads):
    # Print statistics every interval, until all clients have finished
    while len(client_treads) != 0:
        # Wait for the interval
        time.sleep(args.interval)
        # Print the summary
        general_statistics()
        # Remove the threads that have finished
        for client in client_treads:
            if not client.is_alive():
                client_treads.remove(client)


# Description:
#   This function starts the client(s) by the parallel flag
# Parameters:
#   the function takes no parameters in its signature, but it uses the parameters from argparse
#   serverip: the ip of the server to connect to
#   port: the port to use for initiating the connection
#   time: the time to run the client for
#   num: the number of bytes to send
#   interval: the interval to print the summary
#   parallel: the number of parallel clients to run
# Arguments:
#   none
# Returns:
#   nothing, but prints the summary of all the clients running when they are done if interval not set

def start_clients():
    print(formatting_line)
    print(f"A simpleperf client connecting to server {args.serverip}, port {args.port}")
    print(formatting_line)

    # Create a list of threads
    client_treads = []
    # Start the clients with the specified number of parallel clients
    for i in range(0, args.parallel):
        # Start the client
        client = threading.Thread(target=client_start_client)
        client.start()
        client_treads.append(client)

    # Check if an interval is set, if not wait for all clients to finish, then print the summary
    if args.interval is None:
        # Wait for all clients to finish
        for client in client_treads:
            client.join()
        # Print the summary
        general_statistics()
    else:
        interval_timer(client_treads)
    # Wait for all clients to finish adding their transmissions
    time.sleep(0.5)
    print_total()


# Description:
#   This is the main function it starts the server or the client depending on the arguments
# Parameters:
#   the function takes no parameters in its signature, but it uses the parameters from argparse
#   server: a boolean that is true if the user wants to run in server mode
#   client: a boolean that is true if the user wants to run in client mode
#   serverip: the ip of the server to connect to
#   port: the port to use for initiating the connection
#   time: the time to run the client for
#   num: the number of bytes to send
#   interval: the interval to print the summary
#   parallel: the number of parallel clients to run
# Arguments:
#   none
# Returns:
#   nothing, but it will print errors if the arguments are invalidly used
def main():
    # Check if server and client are both set, or none of them
    if (args.server and args.client) or (not args.server and not args.client):
        print_error("You must run either in server or client mode")
        parser.print_help()
        exit(1)

    if args.server:
        # Error checking for server mode, check if user used any client arguments
        server_args_invalid = False

        # Check if user used bind to set server ip
        if args.serverip != default_ip:
            print_error("Wrong use of serverip, use bind to set server ip, while using server mode")
            server_args_invalid = True

        # Check if user used time
        if args.time != default_time:
            print_error("Time argument cant be used in server mode")
            server_args_invalid = True

        # Check if user used an interval
        if args.interval is not None:
            print_error("Interval argument cant be used in server mode")
            server_args_invalid = True

        # Check if user used parallel
        if args.parallel != default_parallel:
            print_error("Parallel argument cant be used in server mode")
            server_args_invalid = True

        # Check if user used num
        if args.num is not None:
            print_error("Number of bytes to send cant be used in server mode")
            server_args_invalid = True

        if server_args_invalid is True:
            parser.print_help()
            exit(1)
        # Finally, start the server if we have no errors
        start_server()
    # End of server mode

    if args.client:
        client_args_invalid = False

        # Error checking for client mode, check if user used any server arguments
        if args.bind != "127.0.0.1":
            print_error("Wrong use of bind, use serverip to set server ip, while using client mode")
            client_args_invalid = True

        # Check if user used both time and number of bytes to send
        if args.num is not None and args.time != default_time:
            print_error("You must specify either number of bytes to send or time to send for")
            client_args_invalid = True

        if client_args_invalid is True:
            parser.print_help()
            exit(1)

        # Start the client(s)
        start_clients()
        # End of client mode


# Start the main function
if __name__ == "__main__":
    main()
