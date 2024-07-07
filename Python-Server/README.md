# Python Server API
===================================
## Table of Contents
- [Python Server API](#python-server-api)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
    - [Socket Manager](#socket-manager)
    - [Network Manager](#network-manager)
    - [UART Manager](#uart-manager)
    - [Data Flow Diagram](#data-flow-diagram)
  - [Code Structure](#code-structure)
    - [Python\_Server.py](#python_serverpy)
    - [socket\_manager.py](#socket_managerpy)
    - [uart\_manager.py](#uart_managerpy)
    - [network\_manager.py](#network_managerpy)
    - [node.py](#nodepy)
    - [message\_opcodes.py](#message_opcodespy)
    - [web\_socket\_proxy\_server.py](#web_socket_proxy_serverpy)
  - [Network Commands](#network-commands)
    - [Overview](#overview-1)
    - [Network Module Commands](#network-module-commands)
    - [Network Server Commands](#network-server-commands)
  - [Defult Message Opcodes](#defult-message-opcodes)
  - [Uart Signal Encoding Scheme](#uart-signal-encoding-scheme)
  - [Node Structure (not sure if needed)](#node-structure-not-sure-if-needed)
  - [References](#references)

## Overview

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

## Code Structure

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
[I (Yudi) will rephrase it later, below is outdated, I (Honghui) can do it after ESP documentation]
Network command is defined to use 5 bytes encoding the operation in network module or python server.

### Overview
```py
############################# Overview #######################################
#
# I. Network Command supported by ESP module
#   (Commands will pass down to and executed in ESP module)
#   'SEND-' send message without ESP module tracking delivery confirmation
#   'SENDI' send and tracks message, retransmit up to 3 times with higher TTL
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
#   (Additional Commands invoiving network monitor)
#   'W-LOG' log message to network monitor
#   'W-RBT' update robot status to network monitor
#
```

### Network Module Commands
```py
############################## Details #######################################
#
# I. Network Module Commands (base commands supported by network module)
#
#   1) Messaging Commands ('SEND-', 'SENDI', and 'BCAST')
#       Delivers an message between devices ( root-api <--> edge device-api )
#       
#       => (Sender) Root-client-API / Edge-client-API Sends:
#         | messaging_command | dst_node_addr |      payload      |
#         |      5 byte       |     2 byte    |    message bytes  |
#
#       <= (Reciver) Edge-client-API / Root-client-API Receives:
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

#       Response to command execution to APIs
#         'S' or 'F|error_msg_size|error_msg'
#
#   3) Query Commands ('NINFO', 'STATE') (TB Finish)
#        (TB Finish)
#        (TB Finish)
#
```

### Network Server Commands
```py
###############################################################################
#
# II. Network Server Commands (additional commands supported by network manager server)
#
#   1) 'NINFO' - Overwrites the 'NINFO' from module, process and return network
#                information.
#       => Root-client-API Sends:
#         | net_info_command |
#         |     5 bytes   |
#
#       <= Root-client-API Recives response from Server:
#         Not Applicable. This command as designed but not implmented since
#         'NSTAT' command below provides basic network status already, choices
#         of intersted network infomation data remain determine.
#
#
#   2) 'NSTAT' - Get all node's information
#       => Root-client-API Sends:
#         | node_info_command |
#         |      5 bytes      |

#       <= Root-client-API Recives Json response from Server:
#         | 'S' success_flag | Json_encoded_data |
#         |      1 byte      |        n          |
#
#        Json Object format:
#          network_status = {
#              "node_amount" : 0,
#              "node_addr_list": [],
#              "node_status_list": []
#          }
#
#
#   3) '[GET]' - Get latest data of node/nodes
#       => Root-client-API Sends:
#         | get_command | data_ID | node_addr |
#         |    5 bytes  |    1    |   2 bytes |

#       <= Root-client-API Recives response from Server:
#         | error_flag | payload |
#         |   1 byte   |    n    |
# 
#        Success:
#         | 'S' | data_ID | data_length (L) | node_amount (N) | node_addr_0 | data_0 | ... | node_addr_n | data_n | 
#         |  1  |    1    |        1        |        1        |      2      |    L   | ... |      2      |    L   |
#
#        Faild:
#         | 'F' | length (L) | Error_Message |
#         |  1  |     1      |       L       |
#
#
#   4) 'ACT-C' - Get amount of active node
#       => Root-client-API Sends:
#         | count_command |
#         |     5 bytes   |
#
#       <= Root-client-API Recives response from Server:
#         | error_flag | payload |
#         |   1 byte   |    n    |
# 
#        Success:
#         | 'S' | active_node_count | 
#         |  1  |         1         |
#
#        Faild:
#         Not Applicable

#   # note: commands involing network monitor
#   5) 'W-LOG' - Log message to network monitor
#       => Root-client-API Sends:
#         |  command  | message |
#         |  5 bytes  |    n    |

#       => Root-client-API Recives:
#         | 'S' |
#
#
#   6) 'W-RBT' - Update robot status to network monitor
#      (Beta version, remain more testing)
#       => Root-client-API Sends:
#         |  command  | payload |
#         |  5 bytes  |    n    |
# 
#         payload format (python list):
#           [
#              { "id": 1, "name": "Robot Node 1", "state": "Active", "node": 'Node-0' },
#              { "id": 2, "name": "Robot Node 2", "state": "Active", "node": 'Node-1' },
#              ...
#           ]
#
#       => Root-client-API Recives:
#         | 'S' |
```
## Defult Message Opcodes

``` python
# =============== Opcode Detiles and Payload Format ================
#
# ******** MESSAGE DEFULT STRUCT *******
#     Msg_meta        |       Msg_Payload
#  2_byte_node_addr   |   1_byte_opcode + payload
# *******************************************
#
# Most message is delevierd between root-APIs <-> edge APIs, they will not stop
# at python-server and gets propogate to application level via Socket.
#
# Message with "Special opcodes" from edge APIs will get processed by 
# Python-Server and DON'T get propogate to application level.
#
# 1) Data Update from edge-API (Special case)
#    Incoming data update get handler in python server
#       => Edge-client-API Sends Message:
#         | 'D' | amount | data_ID | data | ... | data_ID | data |
#         |  1  |    1   |    1    |   L  | ... |    1    |   L  |
#
#       note: data length (L) is pre-defined in "Data_Info.json" and shared 
#             accross devices.
#
```

## Uart Signal Encoding Scheme
```py
# =========================== uart encoding ================================ (TV Review)
#
# **** UART Reserved Bytes ***
# \ff - start of transmission
# \fe - end of transmission
# \fa - escape byte
# \fb to \fd - reserved but not used
# 
# ex: byte \ff will be encode and transmite as \fa\05 (2 encoded byte)
#   encode: \fa Xor \ff = \05
#   decode: \fa Xor \05 = \ff
```

## Node Structure (not sure if needed)
```py
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
```

## References
[do we have reference?]
