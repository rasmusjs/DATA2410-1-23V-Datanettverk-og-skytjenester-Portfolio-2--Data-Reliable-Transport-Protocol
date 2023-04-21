import argparse
import socket
import threading
import time
import re
import sys

# Global variables
formatting_line = "-" * 45  # Formatting line = -----------------------------


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

# Default values
default_ip = "127.0.0.1"
default_time = 25
default_parallel = 1
default_port = 8088

# Client only arguments
client_group = parser.add_argument_group('client')  # Create a group for the client arguments, for the help text
client_group.add_argument('-c', '--client', action="store_true", help="Start in client mode")
client_group.add_argument('-I', '--serverip', type=check_ipaddress, default=default_ip,
                          help="Server ip address to connect to, in dotted decimal notation. Default %(default)s")
# Server only arguments
server_group = parser.add_argument_group('server')  # Create a group for the server arguments, for the help text
server_group.add_argument('-s', '--server', action="store_true", help="Start in server mode")
server_group.add_argument('-b', '--bind', type=check_ipaddress, default=default_ip,
                          help="Bind the server to a specific ip address, in dotted decimal notation. Default %("
                               "default)s")

# Common arguments
parser.add_argument('-p', '--port', type=check_port, default=default_port,
                    help="Port to use, default default %(default)s")

# Parses the arguments from the user, it calls the check functions to validate the inputs given
args = parser.parse_args()


def start_server():
    print("Starting server")


def start_client():
    print("Starting client")


# Startet med arparse. Det er fortsatt ikke helt opplagt hva flaggene er, men jeg antar at -m og -r er de samme greiene.
# -m flagget: server og -r flagget: client
def main():
    parser = argparse.ArgumentParser(description="DRTP file transfer application script")
    parser.add_argument("-c", action="store_true", help="Run in client mode")
    parser.add_argument("-s", action="store_true", help="Run in server mode")
    parser.add_argument("-f", type=str, help="Name of the file")
    parser.add_argument("-m", type=str, choices=["stop_and_wait", "gbn", "sr"], help="Choose Reliability mode in the Server")
    parser.add_argument("-r", type=str, choices=["stop_and_wait", "gbn", "sr"], default="stop_and_wait", help="Choose Reliability mode in the Client")
    parser.add_argument("-t", type=str, choices=["loss", "skipack"], help="Choose your test mode")
    parser.add_argument("-p", type=int, help="Port number")

    args = parser.parse_args()

    if args.c and args.s:
        print("Cannot run as both client and server!")
        sys.exit(1)

    if args.c:
        run_client(args.port, args.f, args.r, args.t)
    elif args.s:
        run_server(args.port, args.f, args.m, args.t)
    else:
        print("Error, you must select server or client mode!")
        sys.exit(1)

if __name__ == "__main__":
    main()