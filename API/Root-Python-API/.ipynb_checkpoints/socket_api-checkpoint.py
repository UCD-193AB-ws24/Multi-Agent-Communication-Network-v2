import threading
import socket
import time
from datetime import datetime

# define constents
SOCKET_OPCODE_LEN = 5     # can be veried base on need
SOCKET_NODE_ADDR_LEN = 2  # need to be 2
socket_op_amount = 2

# example
# node_addr = struct.unpack('!H', node_addr)[0] # unpack 2 byte and converts them from network byte order to host byte order


class Socket_Manager():
    def __init__(self, server_addr, client_socket_callback):
        # set up the parameters
        self.client_socket_callback = client_socket_callback
        pass
        
    def run_socket_listen_thread(self):
        # creat threads, attach callback
        pass
    
    def socket_listening_thread(self):
        # actual thread function responsible for
        # - connect main listen socket
        # - triger callback when there is message
        # - reconnect the main listen socket when fail
        # - close the socket when finish (use finally so it close on exception as well)
        pass
    
    def craft_message_example(self, socket_opcode, node_addr, msg_payload) -> bytes:
        # return the bytes of crafted message
        pass
    
    def socket_sent(self, data: bytes) -> bytes:
        # return the responsed bytes or Fail bytes
        # connect a new one-time use send socket
        pass
    
    def connect_socket(self, server_addr) -> socket.socket:
        # return a connecetd socket or None for fail to connect
        pass
    

# def encode network endianess handler function

# def unpack network endianess handler function
    
    
# other utility function provide by our API

def getOpCodeNum(opcode):
    pass

def parseNodeAddr(addr_bytes: bytes):
    # parse 2 byte into number
    pass