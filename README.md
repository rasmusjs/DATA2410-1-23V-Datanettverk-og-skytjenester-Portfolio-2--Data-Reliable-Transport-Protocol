# Portfolio 2:

## DRTP - Data Reliable Transport Protocol

### Prerequisites

To run our code applications.py, you'll need **Python3** installed on your system. In order to use it in the mininet topology, you'll need to run the **simple_topo.py** code in Ubuntu (22.04/20.04/18.04).

Once you are in Ubuntu, make sure to open the terminal and install mininet:

`sudo apt-get install mininet`

If necessary, make sure to also install openvswitch:

`sudo apt-get install openvswitch-switch`

`sudo service openvswitch-switch start`

For our implementation, we are going to communicate with network devices with the help of xterm, so make sure to install it:

`sudo apt-get install xterm`

## How to run DRTP:

To run DRTP, you MUST run it in either server mode or client mode.

### How to run the server:

If you wish to run simpleperf server with its default values, write the following into a terminal: python3 simplperf.py -s 
It will default to your localhost 127.0.0.1 ip address with default port number 8088 and be in MB format.
If not, you can configure it yourself by raising flags such as:

* -i or --ip: Select the ip address of the server's interface. Example: `python3 simpleperf.py -s -b 127.0.0.1`
* -p or --port: Select the port that you wish to bind to the server. Example: `python3 simpleperf.py -s -p 5001`
* -sp or --server_save_path: Calls upon check_save_path() to check where we have saved the file we want to transfer. Either B, KB or MB. Example: `python3 simpleperf.py -s -f KB`
* -m or --sreliability: Selects the reliability mode on the server side.

If you wish to configure simpleperf and raise all the flags, you may do so. Example: `python3 simpleperf -s -b 127.0.0.1 -p 5001 -f KB`

### How to run the client:

We assume that the server is up and running in a separate terminal. You can run the client with its default values, write the following into the terminal: `python3 simpleperf.py -c`
It will default to the same ip, port number and format as the server default and it will also run a default timer of 25 seconds.
In our script, both -b and -I have the same default ip address of 127.0.0.1 as well as the same -p port number 8088.
If you wish to change the default, make SURE that both ip addresses and port number match, or else you won't be able to establish a connection.

* -i or --ip: Connect the client to a specified server IP address. Example: `python3 simpleperf.py -c -I 127.0.0.1`
* -p or --port: Port number of the server that the client connects to. Example: `python3 simpelperf.py -c -p 5001`
* -f or --file: Select Which format you want the server data transfer be in. Either B, KB or MB. Example: `python3 simpleperf.py -c -f KB`
* -r or --creliability: Selects the reliability mode on the client side. Example: `python3 simpleperf.py -c -i 5`
* -t or --mode: Specify which test we want to run when we transfer our data. Example: `python3 simpleperf.py -c -P 5`

On the client side, you can run most flags simultaneously except for -n, -i and -P. 
You can run -P and -i simultaneously, but do bear in mind that it can yield hard to read results.
I would recommend you run all three -n, -i and -P separately to test their configurations in an optimal way.
Running -t and -n at the same time will also just default to -n.

Except for -n, you can run -t with both -i and -p

Example with -i and -t:

`python3 simpleperf.py -c -I 127.0.0.1 -p 5001 -i 1 -t 5`

`python3 simpleperf.py -c -I 127.0.0.1 -p 5001 -P 3 -t 3`

## How to run the tests in the mininet topology via Simpleperf:

After starting mininet in the terminal in Ubuntu along with all its installations such as xterm. Open up the network entities that you are interested in measuring.
It could be hosts h1 or maybe it could be routers. If you want to take network measurements of the connection from host h1 - h4 you can write the following in mininet:

`xterm h1 h4`

This will open up two terminals where you can choose which host you want to be the server terminal and which one the client.
Find the right directory that simpleperf is located at and run simpleperf as instructed in this Readme. If you want to store the results from measuring network throughput from h1 - h4 you can write the following in the h1 terminal after starting a server in h4:

`python3 simpleperf.py -c -t 2 > throughput_h1-h4.txt`

This will store your data in a .txt file via a standard out data stream.

You can store whatever you want and eventually compare your results to iperf if you wish to do so.
