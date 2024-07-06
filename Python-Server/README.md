# Python Server / client API
===================================
## Table of Contents
- [Python Server / client API](#python-server--client-api)
  - [Table of Contents](#table-of-contents)
  - [Python Server Overview](#python-server-overview)
    - [Socket Manager](#socket-manager)
    - [Network Manager](#network-manager)
    - [UART Manager](#uart-manager)
    - [Data Flow Diagram](#data-flow-diagram)
  - [Python Server Files](#python-server-files)
    - [Python\_Server.py](#python_serverpy)
    - [socket\_manager.py](#socket_managerpy)
    - [uart\_manager.py](#uart_managerpy)
    - [network\_manager.py](#network_managerpy)
    - [node.py](#nodepy)
    - [message\_opcodes.py](#message_opcodespy)
    - [web\_socket\_proxy\_server.py](#web_socket_proxy_serverpy)
  - [Network Commands](#network-commands)
  - [Defult Message Opcodes](#defult-message-opcodes)
  - [References](#references)

## Python Server Overview

The python server act as a gatewall to relay the message exterior to the network module into the module. It ensures asynchronous communication can be maintain with multiple threads running. The server also implements the reconnection logic and caches data from edge nodes for quicker access when data are request by the client API. The python server consist of three main components, The `Socket Manager`, the `Network Manager`, and the `UART Manager`. 

### Socket Manager
The `Socket Manager` handles the communication between the python server and the client API through socket since both process will be running on the same operating system. It will open a listening socket and accept incomming connection on a new thread. Upon receiving the connection, it will first check which type of the connection it is. The socket expect two type of connection to be connected from the client API. First  type of connection is `listening connection`, this listening connection is designed for the `Client API` to listen to any message sending from the Python Server. THe `listening connection` is established through a handshake. When `listening connection` is not established, all the incomming connection will be check for handshake before connection. THe second type of the connection is `sending connection`, which is used by the `Client API` to send inbounding communication to the network module. Each Client message is will open a individual  `sending connection`, that will be closed immediately after receiving expected response. 

In our design, when the client sending any request to the network module, the response can be received in two way. the response to special costom message that may need real time response from the edge node will send through the `listening connection` so the `sending connection` of that request can close earlier free up a thread on the client's program sooner. Since `listening connection` on the `client API` side also supports event handler, it's better for the message from the network module to be passed to the `Client API` through `listening connection`. On the other hand, a response 
addressing the simbple data request will be send back through the `sendinig connection` that send the request in the first place, because data is cached in our python server

### Network Manager
The network manager pass on the message between UART Manager and Socket Manager. Since the the Socket Manager and the UART Manager are in the different thread, the Network Manger need to communicate through callback function. When the Network Manager need to pass the message to Socket Manager or UART Manager, it need to call the callback function from the respective manager that were passed in during the initialization. When the Socket Manager and the UART Manager need to pass message to the Network Manager, they will called the callback function defined within the Network Manager.
[possible example code here?]


### UART Manager
The UART Manager first Scan the serial ports of the machine to detect a UART port, the Python library automatically handles reading  and writing. When a message is received it will be decoded and triggles the callback function defined in the `Network Manager` class to update the node data or further pass the message to the `Socket Manager`

### Data Flow Diagram
[insert picture here, that one picture Yudi made just need some tweek, and fix the mistake on the sockets]

##  Python Server Files

### Python_Server.py
Setup an instance of three class with the correct callback function then launches the socket communication thread and the Uart communication thread

### socket_manager.py
Contans the socket manager class that initialize the socket, it accept an callback function during initialization and that callback function will be called when the Socket Manager receive a new message. In our use case this callback function is a function in the Netowrk_Manager class to pass onto the Network Manager . It also contains a function that will be callbacked by the Network_manager when the Network Manager need to pass on the message.

### uart_manager.py
Contains the UART manager class. The initialization of the class accept an callback call that will be called when a message is received through the UART serial port handles the connections from the root. The class also defines a callback function that will be used by the network manager when a message need to be send to root. It also handles the decoding and encoding logic of the UART message.  

### network_manager.py 
Contains a network manager class that will be launched, the network manager will be mainly used as a switch that process and relay the message from UART manager to Socket Manager or vice versa. This is done through the callback function from UART manager and Socket Manager that's passed in the network manager have the following feature
* Getting a list of active nodes
* Getting the data of a node with specified id and node address
* Update the node data of a existing node
* Handles inbound command from API  to the network where it can choose relay the message onto the root node or process it locally. 
* Handles the outbound communication from  to the network where it can choos
* Supporting webscoket extennsion for further extension such as monitoring

### node.py
Contain class that defines a edge node with the following feature:
* Each data store all it's history infomation in a queue with timestamp
* Supports multiple data types being stored at the same time
* Supports inforomation lookup and update on specific data type

### message_opcodes.py
Contains a structure for current opcodes that can be easily add on

### web_socket_proxy_server.py
[need help]


## Network Commands
[I (Yudi) will rephrase it later, below is outdated, I (Honghui) can do it after esp documentation]
Network command is defined to use 5 bytes encoding the operation in network module or python server.
``` python
############################# Overview #######################################
# I. Network Command supported by esp module
#   (Commands will pass down to and executed in esp module)
#   'SEND-' send message without esp module tracking delivery confirmation
#   'SENDI' send and tracks message, retransmit up to 3 times with higher ttl
#   'BCAST' broadcast message
#   'RST-R' restart root module
#   'CLEAN' clean and reset the network in persistent memoory
#   'NINFO' get network info in bytes
#   'STATE' get node connection state in edge module (only for Edge-API)
#
# II. Network Command supported by network server
#   (Additional Commands will executed network server)
#   'NINFO' get network info and process to json format
#   'NSTAT' get node status
#   '[GET]' get node data
#   'ACT-C' get active node count
#
############################## Detiles #######################################
#
# I. Networok Module Commands (base commands supported by network module)
#
#   1) Messaging Commands ('SEND-', 'SENDI', and 'BCAST')
#       Delivers an message between devices ( root-api <--> edge device-api )
#       
#       => Root-client-API / Edge-client-API Sends:
#         | messaging_command | dst_node_addr |      payload      |
#         |      5 byte       |     2 byte    |    message bytes  | 
#
#       <= Edge-client-API / Root-client-API Receives:
#         | src_node_addr |      payload      |
#         |     2 byte    |    message bytes  |
# 
#       Response to command execution to APIs
#         'S' or 'F|error_msg_size|error_msg'
#      
#   note: for 'BCAST' 2 byte dst_node_addr is just place holder and not getting
#         used in sendding, put 0 as dst_node_addr is sufficient since it align
#         with "selecting all node" in other commands.
#
#   2) Operation Commands ('RST-R', 'CLEAN')
#       Order module to perform corresponded operation, no payload needed
#         | messaging_command |      payload      |
#
#   3) Query Commands ('NINFO', 'STATE') (TB Finish)
#
# II. Networok Server Commands (additional commands supported by network manager server)
#
#   1) 'NINFO'
#
#
#   2) 'NSTAT'
#
#
#   3) '[GET]'
#
#
#   4) 'ACT-C'
#





# bleow is the raw design note that need to be clean and reformat




#
# =========================== API protocal ================================ detile case for each command (TB Finish)
# Struct: 5_byte_command | payload
# 
# ===== Get Data =====
# => incoming command
# [GET]|data_type|node_addr/index // Need to chaneg to node_addr|daya_type  ------------------------- "TB Finish" -------------------------
#
# <= response (single or patch)
# S|data_type|data_length_byte|size_n|node_addr/index_0|data_0|...|node_addr/index_n|data_n
# OR
# F|message_size|Error_flag/Message
#
# ===== Network Status Query =====
# => incoming socket Network Status Query
# NETIF|state   - states are A:active, D:disconnected, N:not avaiable ...
#
# <= responde nodes with that state
# S |node_amount|node_0_addr|node_0_uuid|....|node_n_addr|node_n_uuid
# 1 |     1      |   2 byte  |  16 byte  |....|   2 byte  |  16 byte  |
# OR
# F|message_size|Error_flag/Message
#
# ===== Send to edge ===== (direcly pass to esp-root module for execution)
# => incoming command
# SEND- | dst_node_addr  | message
# BCAST | 2_byte_padding | message
#
# <= response
# 'S' or 'F|msg_size|Error_msg'
# 
#
# =========================== API Message special opcodes ================================ detile case for each defulet messages (TB Finish)
# speicla opcodes don't pass to the other side of API but got take cared by Python-Server
#
# ******** Special opcode KEY STRUCT *******
#     Msg_meta        |       Msg_Payload
#  2_byte_node_addr   |   1_byte_opcode + payload (defult format)
# *******************************************
#
# (uart) ===== Root Full Reset =====
# => incoming 
# root_addr|RST_opcode|
#    2     | 1 |
#
# (uart) ===== Data Update from edge-API =====
# => incoming data update
# node_addr|Data_Update_opcode| size_n|data_ID|data| ... |data_ID|data|
#    2     | 1                |   1   |   1   | xx | ... |   1   | xx | 
#
# (uart) ===== Network Status update from esp-root ===== (TB Finish)
# => incoming socket Network Status Update
# root_addr|NET| node_amount|node_0_addr|node_0_uuid|....|node_n_addr|node_n_uuid
#    2     | 3 |     1      |   2 byte  |  16 byte  |....|   2 byte  |  16 byte  |
#
# (uart) ===== Node Connecetd update ===== (TB Finish)
# => incoming 
# root_addr|NOD| node_addr | node_uuid |
#    2     | 3 |    2 byte |  16 byte  |
#
# =========================== uart encoding ================================ (TV Review)
#
# **** UART ENCODE ***
# \ff - start of transmission
# \fe - end of transmission
# \fa - escape byte
# 
# ex: byte \ff will be transmite as \fa\05
#   encode: \fa Xor \ff = \05
#   decode: \fa Xor \05 = \ff
#
# =========================== Node Structure ================================
# Pre-Define data type in Json file to save network bandwidth
#   - define name (key), one byte ID, and data length (bytes) for data types
#   - Name is used as key and logging label.
#   - One byte ID is used as identifier in network message
#   - Data length is used in parsing and extracing data bytes from entire message bytes.
#
# Work Pending finish (ctr-f "TB Finish")
# Work Pending review (ctr-f "TB Review")
# Work Pending fix (ctr-f "TB Fix")
# 
# ----------------- wating finishing ----------------------------
#
# - now when a node sends data over, it add node to list if is not already in list, not using name and uuid of nodes!!
# - getNodeStatus
#
#
#
```

## Defult Message Opcodes

``` python
#
# === defult API opcode / message type === (wrong, updated to one byte opcode define in seperate file)
# one byte use to control the message type in application level, is part of message.
#
#
#
```
## References
[do we have reference?]
