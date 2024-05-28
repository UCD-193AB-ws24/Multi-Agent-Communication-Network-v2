``` python
######################################################################################
# === Network Command  ===
# 'NINFO' get network info
# 'SEND-' send message
# 'BCAST' broadcast message
# 'RST-R' reset root module
# 'ACT-C' get active node count
#
# '[GET]' get node data
# 
#
# === API opcode / message type === 
# 'ECH' for echo message, expecting copy
# 'CPY' for copy message on recived 'ECH'  or 
#
# 'NET' Network Information message
# 'NOD' Node Connecetd update message
# 'RST' root module reseted
# '[D]' node data
#
######################################################################################
#
# Design Note
#
# =========================== API Message passing format ================================
# our API one side to ther other (root-api -> edge device-api OR edge device-api -> root-api):
# Root-client-API / Edge-client-API Sends:
# ble_network_command | dst_node_addr |          message        |
#       5 byte        |     2 byte    | 3 byte opcode | payload |
#
# Edge-client-API / Root-client-API Sends:
#   src_node_addr |          message        |
#      2 byte     | 3 byte opcode | payload |
#
# message is the same (client can change opcode & opcode length whatever they want in APP level), address will be dst for sender, src for reciver
# besides the special pre-defined opcodes will get handle by python server, rest will show up on API
#
# =========================== API protocal ================================
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
# =========================== API Message special opcodes ================================
# speicla opcodes don't pass to the other side of API but got take cared by Python-Server
#
# ******** Special opcode KEY STRUCT *******
#               Msg_meta            |     Payload
#  2_byte_node_addr|3_byte_msg_type |     payload
# *******************************************
#
# (uart) ===== Root Full Reset =====
# => incoming 
# root_addr|RST|
#    2     | 3 |
#
# (uart) ===== Data Update from edge-API =====
# => incoming data update
# node_addr|[D]| size_n|data_type|data_length_byte|data|...|data_type|data_length_byte|data
#    2     | 3 |   1   |   3     |     1          | n| ... (size of each segment in bytes)
#
# (uart) ===== Network Status update from esp-root =====
# => incoming socket Network Status Update
# root_addr|NET| node_amount|node_0_addr|node_0_uuid|....|node_n_addr|node_n_uuid
#    2     | 3 |     1      |   2 byte  |  16 byte  |....|   2 byte  |  16 byte  |
#
# (uart) ===== Node Connecetd update =====
# => incoming 
# root_addr|NOD| node_addr | node_uuid |
#    2     | 3 |    2 byte |  16 byte  |
#
# =========================== uart encoding ================================
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