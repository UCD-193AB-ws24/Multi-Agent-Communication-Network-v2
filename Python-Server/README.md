# Python Server / client API
===================================
## Table of Contents

## Overview

## Python Server Overview

The python server act as a gatewall to relay the message exterior to the network module into the module. It ensures asynchronous communication can be maintain with multiple threads running. The server also implements the reconnection logic and caches data from edge nodes for quicker access when data are request by the client API. The python server consist of three main components, The `Socket Manager`, the `Network Manager`, and the `UART Manager`. 

### Socket Manager
The `Socket Manager` handles the communication between the python server and the client API through socket since both process will be running on the same operating system. It will open a listening socket and accept incomming connection on a new thread. Upon receiving the connection, it will first check which type of the connection it is. The socket expect two type of connection to be connected from the client API. First  type of connection is `listening connection`, this listening connection is designed for the `Client API` to listen to any message sending from the Python Server. THe `listening connection` is established through a handshake. When `listening connection` is not established, all the incomming connection will be check for handshake before connection. THe second type of the connection is `sending connection`, which is used by the `Client API` to send inbounding communication to the network module. Each Client message is will open a individual  `sending connection`, that will be closed immediately after receiving expected response. 

In our design, when the client sending any request to the network module, the response can be received in two way. the response to special costom message that may need real time response from the edge node will send through the `listening connection` so the `sending connection` of that request can close earlier free up a thread on the client's program sooner. Since `listening connection` on the `client API` side also supports event handler, it's better for the message from the network module to be passed to the `Client API` through `listening connection`. On the other hand, a response 
addressing the simbple data request will be send back through the `sendinig connection` that send the request in the first place, because data is cached in our python server

### Network Manager
The network manager pass on the message between UART Manager and Socket Manager. Since the the Socket Manager and the UART Manager are in the different thread, the Network Manger need to communicate through callback function. When the Network Manager need to pass the message to Socket Manager or UART Manager, it need to call the callback function from the respective manager that were passed in during the initialization. When the Socket Manager and the UART Manager need to pass message to the Network Manager, they will called the callback function defined within the Network Manager.
[possible example code here]


### 



[insert picture here]

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

## Client API Overview
[Since API is in a different file should this part be in a different folder?]

## Client API Files

## Protocol
[I (Yudi) will rephrase it later]
``` python
# Design Note
# Project Configs
# "[E]" - end of message delimiter, defined in networkConfig
#
#
# =========================== socket protocal ================================
# => incoming
# [CMD]payload
# [GET]|data_type|node_addr/index // Need to chaneg to node_addr|daya_type  ------------------------- "TB Finish" -------------------------
#
# <= data outgoing (single or patch)
# S|data_type|data_length_byte|size_n|node_addr/index_0|data_0|...|node_addr/index_n|data_n
# ^ success
# F|message_size|Error_flag/Message
#
# <= request outgoing
# |request_type|node_addr/index|
#
# =========================== socket protocal ================================
#
# =========================== temp uart protocal ================================
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
# **** UART KEY STRUCT ***
# need to be followed by all uart messsage
#               Msg_meta            ||     Payload
#  2_byte_node_addr|3_byte_msg_type ||     payload
#
#
# **** KEY STRUCT ***
#
# => incoming data update
# node_addr|[D]|| size_n|data_type|data_length_byte|data|...|data_type|data_length_byte|data
#    2     | 3 ||   1   |   3     |     1          | n| ... (size of each segment in bytes)
#
#
# => incoming message
# node_addr|[M]|| size_n| message
#    2     | 3 ||   1   |  n 
#
#
# <= out going command (temp) using '-' as inter_cmd deliminator, '\n' as cmd deliminator
# 5_byte_cmd|payload|'\n'
#
#  * NINFO|'\n'                                                   // get network info
#  * SEND-|2_byte_node_addr|1_byte_msg_len|message/data|'\n'      // send message/cmd to edge
#
# =========================== temp uart protocal ================================
#
# =========================== Node Structure ================================
# Pre-Define: some data type such as GPS
#   - define the data_type key for saving/logging/accessing data
#   - define the length (byte) of data and implments data->data_bytes parseing
#   * "GPS", 6 byte, longtitue|latitude
#
# Dynamic: allow adding other data_type
#   - when the data generated from edge-device it will pass over as byte directly
#   - save as byte and give it to client as byte
#   - So client can define custom data-type 
#     and sync btw their own edge-device code and control-software code
#
# =========================== socket protocal ================================
#
#
# Work Pending finish (ctr-f "TB Finish")
# 
# ----------------- wating finishing ----------------------------
#
# - now when a node sends data over, it add node to list if is not already in list, not using name and uuid of nodes!!
#
#
#
```

## Referneces
