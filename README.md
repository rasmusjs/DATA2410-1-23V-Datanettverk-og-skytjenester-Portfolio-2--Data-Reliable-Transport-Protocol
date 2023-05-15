# Portfolio 2:

## DRTP - Data Reliable Transport Protocol

### Prerequisites

To run our code applications.py, you'll need **Python3** installed on your system. In order to use it in the mininet
topology, you'll need to run the **simple_topo.py** code in Ubuntu (22.04/20.04/18.04).

Once you are in Ubuntu, make sure to open the terminal and install mininet:

`sudo apt-get install mininet`

If necessary, make sure to also install openvswitch:

`sudo apt-get install openvswitch-switch`

`sudo service openvswitch-switch start`

For our implementation, we are going to communicate with network devices with the help of xterm, so make sure to install
it:

`sudo apt-get install xterm`

## How to run DRTP:

To run DRTP, you MUST run it in either server mode or client mode.

### How to run the server:

When running the server, it is mandatory to use the -m or --sreliability flag. This chooses which reliability mode to
use with the UDP. You can either choose "stop_and_wait", "gbn" (go back n) or "sr" (selective repeat).

If you wish to run application.py server with its default ip and port, write the following into a terminal: python3
application.py -s -m <mode>
It will default to your localhost 127.0.0.1 ip address with default port number 8088.
You can choose additional things with the following flags:

* -i or --ip: Select the ip address of the server's interface.
  Example: `python3 application.py -s -i 10.0.2.1 -m <mode>`
* -p or --port: Select the port that you wish to bind to the server.
  Example: `python3 application.py -s -p 5001 -m <mode>`
* -sp or --server_save_path: Chooses where the transferred file is stored
  Example: `python3 application.py -s -sp foldername -m <mode>`
* -m or --sreliability: Selects the reliability mode on the server side as explained further up.

The flags can be used in any order.

### How to run the client:

A client also needs to be ran with either -r or --creliability. This chooses the reliability that the client is going to
run with. You can choose the same reliability that you can choose on the server.

If you wish to run application.py client with its default ip and port, write the following into a terminal: python3
application.py -c -r <mode>

It will default to the same ip and port number as the server default. To establish a connection the server AND the
client need to flag the same port and IP address.

* -a or --serverip: Connect the client to a specified server IP address.
  Example: `python3 application.py -c -i 127.0.0.1 -r <mode>`
* -p or --port: Port number of the server that the client connects to.
  Example: `python3 application.py -c -p 5001 -r <mode>`
* -f or --file: Select the file to send
* -r or --creliability: Select the reliability mode on the client side. Example: `python3 application.py -c -r gbn`
* -t or --mode: Specify which test we want to run when we transfer our data. Can choose either loss or skipack
  Example: `python3 application.py -c -t skip_ack -r <mode> -f <filename>`
* -tn or --tnetem: Specify artificial network conditions, such as packet loss, reorder, duplicates.
  Example: `python3 application.py -c -t skipack -r <mode>`

The flags can be used in any order.

## How to run the tests in the mininet topology via DRTP:

After starting mininet in the terminal in Ubuntu along with all its installations such as xterm. Open up the network
entities that you are interested in measuring.
It could be hosts h1 or maybe it could be routers. If you want to take network measurements of the connection from host
h1 - h4 you can write the following in mininet:

`xterm h1 h4`

This will open up two terminals where you can choose which host you want to be the server terminal and which one the
client.
Find the right directory that DRTP is located at and run DRTP as instructed in this Readme. If you want to store the
results from measuring network throughput from h1 - h4 you can write the following in the h1 terminal after starting a
server in h4:

`python3 application.py -c -m gbn > throughput_h1-h4.txt`

This will store your data in a .txt file via a standard out data stream.
