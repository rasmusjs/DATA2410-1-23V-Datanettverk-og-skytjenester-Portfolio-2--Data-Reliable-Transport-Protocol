# Portfolio 2:

## DRTP - Data Reliable Transport Protocol

### Prerequisites

To run our code applications.py, you'll need **`python33** installed on your system. In order to use it in the mininet
topology, you'll need to run the **simple_topo.py** code in Ubuntu `22.04/20.04/18.04`.

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

#### Server only arguments:

-s, --server Run in server mode `python3 application.py -s`

-sp, --save_path: Save path for the files. If the folder does not exist, it will be created. Default folder
received_files `python3 application.py -s -sp save_folder`

#### Common options:

-h, --help show this help message and exit `python3 application.py -s -h`

-i IP, --ip IP address to connect/bind to, in dotted decimal notation. Default 127.0.0.1 `python3 application.py -s -i
192.168.0.1

-p, --port Port to use, default 8088 `python3 application.py -s -p 9000`

-r {stop_and_wait,gbn,sr}, --reliability {stop_and_wait,gbn,sr}
Choose reliability mode, this must match the server/client reliability mode `python3 application.py -s -r gbn`

-w, --window
Set the window size, default 5 packets per window `python3 application.py -s -w 10`

-t {loss,skip_ack}, --mode {loss,skip_ack}
Choose your a testcase, loss or skip_ack. Skip_ack will run on the server side only, and loss will run on the client
`python3 application.py -s -t loss`

-tn {duplicate,loss,reorder,skip_ack,skip_seq}, --tnetem {duplicate,loss,reorder,skip_ack,skip_seq}
Run tnetem artificial network emulation on the host; it requires root privileges `python3 application.py -s -tn reorder`

The flags can be used in any order.

### How to run the client:

#### Client only arguments:

-c, --client Run in client mode `python3 application.py -c`

-f FILE, --file FILE Name of the file to send `python3 application.py -c -f filename.txt`

#### Common options:

-h, --help show this help message and exit `python3 application.py -h`

-i IP, --ip IP address to connect/bind to, in dotted decimal notation. Default 127.0.0.1 `python3 application.py -i
192.168.0.1

-p, --port Port to use, default 8088 `python3 application.py -p 9000`

-r {stop_and_wait,gbn,sr}, --reliability {stop_and_wait,gbn,sr}
Choose reliability mode, this must match the server/client reliability mode `python3 application.py -r gbn`

-w, --window
Set the window size, default 5 packets per window `python3 application.py -w 10`

-t {loss,skip_ack}, --mode {loss,skip_ack}
Choose your a testcase, loss or skip_ack. Skip_ack will run on the server side only, and loss will run on the client
`python3 application.py -t loss`

-tn {duplicate,loss,reorder,skip_ack,skip_seq}, --tnetem {duplicate,loss,reorder,skip_ack,skip_seq}
Run tnetem artificial network emulation on the host; it requires root privileges `python3 application.py -tn reorder`

#### Common options:

-h, --help show this help message and exit `python3 application.py -c -h

-i IP, --ip IP IP address to connect/bind to, in dotted decimal notation. Default 127.0.0.1 `python3 application.py -c
-i
192.168.0.1

-p PORT, --port PORT Port to use, default 8088 `python3 application.py -c -p 9000

-r {stop_and_wait,gbn,sr}, --reliability {stop_and_wait,gbn,sr}
Choose reliability mode, this must match the server/client reliability mode `python3 application.py -c -r gbn

-w WINDOW, --window WINDOW
Set the window size, default 5 packets per window `python3 application.py -c -w 10

-t {loss,skip_ack}, --mode {loss,skip_ack}
Choose your a testcase, loss or skip_ack. Skip_ack will run on the server side only and loss will run on the client
`python3 application.py -c -t loss

-tn {duplicate,loss,reorder,skip_ack,skip_seq}, --tnetem {duplicate,loss,reorder,skip_ack,skip_seq}
Run tnetem artificial network emulation on the host, it requires root privileges `python3 application.py -c -tn reorder

The flags can be used in any order.

## How to run the tests in the mininet topology via DRTP:


