``` python
# Design Note
# Project Configs
# "[E]" - end of message delimiter, defined in networkConfig
#
#
#
# our API one side to ther other (root-api -> edge device-api OR edge device-api -> root-api):
# Root-client-API / Edge-client-API Sends:
# ble_network_command | dst_node_addr |          message        |
#       5 byte        |     2 byte    | 3 byte opcode | payload |
#
# Edge-client-API / Root-client-API Sends:
#   src_node_addr |          message        |
#     2 byte     | 3 byte opcode | payload |
#
# message is the same (they can change opcode & opcode length whatever they want in APP level), address will be dst for sender, src for reciver
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
# ******** UART KEY STRUCT *******
# need to be followed by all uart messsage
#               Msg_meta            ||     Payload
#  2_byte_node_addr|3_byte_msg_type ||     payload
#
# ********** KEY STRUCT *********
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
# => incoming network info
# root_addr|NET|| node_amount|node_0_addr|node_0_uuid|....|node_n_addr|node_n_uuid
#    2     | 3 ||     1      |   2 byte  |  16 byte  |....|   2 byte  |  16 byte  |
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