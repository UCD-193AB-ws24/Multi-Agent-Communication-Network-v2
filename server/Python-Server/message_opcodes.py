opcodes = {
    # =========== API Message defult opcodes ==============
    "Custom":      b'\x00',      # Guarantee to be pass to app level
    "Net Info":    b'\x01',
    "Node Info":   b'\x02',
    "Root Reset":  b'\x03',      # Singling root just get powered / restarted
    "Data":        "D".encode(), # Data Update message (Spcial usecase description below)
    "Request":     "R".encode(), # Request message, such as robot request
    "ECHO":        "E".encode(), # message expecting ECHO message back
    "ACK":         "A".encode(), # Acknowledgement message as confirmation on receivion
    "Test":        "T".encode(), # Reserved for develpoment testing message
    "Reset":       "S".encode(), # Message to inform edge device reset edge-esp-network-module
    # ============= End of defult opcodes =================
}

# =============== Opcode Detiles and Payload Format ================
# Most message is delevierd between root-APIs <-> edge APIs, they will not stop
# at python-server and gets propogate to application level via Socket.
#
# Message with "Special opcodes" from edge APIs will get processed by 
# Python-Server and DON'T get propogate to application level.
#
# ******** MESSAGE DEFULT STRUCT *******
#     Msg_meta        |       Msg_Payload
#  2_byte_node_addr   |   1_byte_opcode + payload
# *******************************************
#
# 1) Data Update from edge-API (Special case)
#    => incoming data update get handler in python server
# node_addr|Data_Update_opcode| amount |data_ID|data| ... |data_ID|data|
#    2     |        1         |    1   |   1   | xx | ... |   1   | xx | 
#
