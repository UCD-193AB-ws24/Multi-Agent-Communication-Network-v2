# Python Server API
===================================


## Table of Contents
just empty for now, easy to add



## Overview

### I. Role of Network Server
The `Network Server (Python)` serves as the middle layer between `client software` and the `network module`. It provides additional `application-level services` such as storing `mesh network status`, caching `edge device's latest data`, performing additional processing at the application level, and more. The `Network Server` aims to abstract away `BLE mesh network` management from the client software and reduce the latency of data queries by caching the latest data updates to avoid the round trip time to the edge node.

Note: The `Network Server` is not required to use the network module. Direct communication using `UART` with the module can still access the network.

### II. Message flow Overview
Serves as middle support layer between client software and network module. (updated to image after)

1) Operations pass down to the network module. 
    - ex: sending a message to edge
```py
  API <---socket---> python server <---uart---> module
```

2) Operations executed in server directly
    - ex: Get the latest data on a certain note
```py
  API <---socket---> python server
```

## Python Server Setup (TB Finish)
 - operating system 
   - only work in Linux for now due to socket and USB port access
 - python lib installation (requirement.txt)
   - pip install -r requirements.txt
   - tested working on Python 3.10
 - command to lunch server
   - run `python3 Python_Server.py` in folder `Multi-agent-Communication-Network/Python-Server`

------------------- then details in how to set up API --------------------

## 1) Python Server Interface design
  - Socket Communication   (API <--> Server communication channle and structure)

### Overview
  - chart needed

### I. establish connection

### II. main server -> API socket (rewording needed)

### III. mutiple send API -> server socket (rewording needed)

------------------- then details in how to talk to APIs --------------------

## 2) Protocol (rewording might needed)
The protocol to interact with the python server and network module is defined to consist `5_byte_network_command | payload` where the payload's format varys based on the command.

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

### I. Network Module Commands
Commands that are executed in network module, which server will propogate the command to esp32 network module.
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

### II. Network Server Commands
Additional commands that are executed in network server.
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

### III. Defult Message Opcodes
Application level message type inditification. Most message is delevierd 
between root-APIs <-> edge APIs, they will not stopat python-server and gets 
propogate to application level via Socket.
``` python
# ******** MESSAGE DEFULT STRUCT *******
#     Msg_meta        |       Msg_Payload
#  2_byte_node_addr   |   1_byte_opcode + payload
# *******************************************
```

Message with "Special opcodes" from edge APIs will get processed by 
Python-Server and DON'T get propogate to application level.

``` python
# ========================== Special Message Opcode ===========================
# 1) Data Update from edge-API (Special case)
#    Incoming data update get handler in python server
#       => Edge-client-API Sends Message:
#         | 'D' | amount | data_ID | data | ... | data_ID | data |
#         |  1  |    1   |    1    |   L  | ... |    1    |   L  |
#
#       note: data length (L) is pre-defined in "Data_Info.json" and shared 
#             accross devices.
```

### IV. Network Endianess
  - byte order of addresses used network endianess.

### Example
 - actual bytes of and command as example
------------------- then details in how server works --------------------

## 3) Python Server Internal Logic (Server Internal Logic Flow)

### Overview

The python server followers the OOP design and modularizes the core logic into three class. The `Socket Manager` class handles the communication with the users program through device sockets with the provided `Root-Python-API`. The `Network Manager` handles the main Server logic that store and manages the edge node data. The `Uart Manager` class handles the communication with the root esp module through the serial port that runs UART protocol. 

Whenever the `Socket Manager` or the `Uart Manager` received a message, they need the logics in `Network Manager` for processing the message in the next step. The corresponding callback function defined in the `Network Manager` is called to conceptually passed on the logic onto the network manager module. Similarily, when `Network Manager` class is ready to send the processed message through either the socket or UART serial connection, it will call the appropriate callback function defined in either the `Socket Manager` or the `Uart Manager`.

The design of the callback function is to keep the logic contain in the correct module. It's a form of event handler that handles the event that requires borrowing the logic assigned in the other module.

### Python_Server.py
The purpose of this file is to etup an instance of each of three class with the correct callback function attached. Then it will launches the required threads. The threads in the `Uart Manager` and the `Socket Manager` are dedicated for the socket and the serial port connection. The threads in the `Network Manager` is just for the main thread to keep the program from exiting.

The Following are the adjustible variable for further configuration of the python server:
- PACKET_SIZE: The maximum size of the packets that can be received through the socket connection.
- server_socket_port: The port used for binding the python server socket that will be used by the provided API.
- proxy_server_port: The port used for web socket for hostiing a proxy server, this can be used for the extension of some monitory programs.
- port: Indicate the type of serial port, in default case '/dev/ttyUSB0' indicates a USB-to-serial adapter.
- baud_rate: The Baud_rate for the UART used in the connection with the Root esp node
- log_folder: The path of the file for logging the node datas.

### Class Objects
#### 1) Socket Manager
The `Socket Manager` handles the communication between the python server and the user's program through sockets, since both process will be running on the same device. It will open a listening socket and accept incoming connections. Upon receiving a connection, it will first check which type of connection, because there are two types of connections that can be expected. First, the manager need to initiate the socket. Then it needs to launch a thread to keep the socket open for accepting incomming connections.

The first type of connection is the `listening connection`. This listening connection is setup for the user program to listen to the majority of the messages sent from the Python server. The `listening connection` is identified and established through a handshake. When a `listening connection` is not established, all incoming connections will be checked for a handshake before connection. When the `listening connection` failed from the user end and need to be reconnected, this handshake is also very important for the python server to be ready for the reconnection of the `listening connection`. 

The second type of connection is the `sending connection`, which is used by the user program to send message to the python server. Each message will open an individual `sending connection`, which will be closed immediately after receiving the expected response. Any request from the user will be send through this type of the connection. 

In our design, when the client sends any request to the python server, the response can be received in two ways. The response addressing the special custom messages that may need a real-time response from the edge node will be sent back through the `listening connection`, so the `sending connection` of that request can close earlier, freeing up a thread on the users program sooner. Since the provided user API supports event handlers on the  `listening connection`, it is also more flexible for the custom response from the network module to be respond back to the user through the `listening connection`. 

On the other hand, a response addressing a simple data request will be sent back through the `sending connection` that sent the request in the first place, because the data is cached on our Python server and does not waste the time and thread resource of the user.

#### 2) Network Manager
The `Network Manager` is used when a message is passed in from either the socket or the UART port. The core purpose of the `Network Manager` is to manage the node data and overall network information. All the edge nodes update the data of a node whenever there is a new update, independent of the user's request. When new data is received, it updates the node status or the data of the corresponding node.

The `Network Manager` maintains a list of nodes that is globally accessible to all other classes. Each node keeps a deque of (data, time) pairs. The purpose of the deque is to log the history of each data. When the user requests a data update through the `sending connection` and the `Socket Manager` calls a callback function defined by the `Network Manager`, the `Network Manager` will search through the list of nodes and their histories to get the most recent data. Then, it passes the data request or the network request back through the same `sending connection`.

[talking about parsing the address]

#### 3) Uart Manager
[talk about scan, read, write]

[talking about start and ending bytes]

### Detailed Callback Functions Flow
  - should propably include in python code file itself? or introduce in certain degress in readme as well?

### Utility functions / files
#### 1) node.py
Contain class for edge nodes with the following characteristics and features:
* Each data store all it's history infomation in a queue with timestamp
* Supports multiple data types being stored at the same time
* Supports inforomation lookup and update on specific data type

#### 2) message_opcodes.py
Contains a structure for current opcodes that can be used. It can be modified and extended.

#### 3) History log folder
####Network endianess



----------------------- raw documentations from before --------------------------------

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
