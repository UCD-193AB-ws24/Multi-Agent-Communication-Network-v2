import serial
import threading
import time

# ==== protocal constents ====
escape_byte_bs = b'\xfa' # byte string of 0xfa
escape_byte = escape_byte_bs[0] # int type == 0xfa == 250
uart_start = b'\xff'
uart_end = b'\xfe'

class Uart_Task_Manager:
    def __init__(self, uart_port, uart_baud_rate):
        self.uart_port = uart_port
        self.uart_baud_rate = uart_baud_rate
        self.serial_connection = None
        self.uart_thread = None
        self.callback_func = None
        
        self.uart_connect()
            
    def uart_connect(self, uart_port, uart_baud_rate):
        # close current port
        if self.uart_port != uart_port and self.serial_connection != None:
            self.serial_connection.close()
            self.serial_connection = None
        
        self.uart_port = uart_port
        self.uart_baud_rate = uart_baud_rate
        self.connect()
            
    def uart_connect(self):
        if self.serial_connection != None:
            print("Uart port already connected:", self.uart_port)
            return
        
        # try connect to new port
        try:
            self.serial_connection = serial.Serial(self.uart_port, self.uart_baud_rate)
            print("connected to serial port", self.uart_port)
        except:
            print("unable to connect to serial port", self.uart_port)
        
        
    def uart_event_handler(self, data):
        # print("recived uart data:")
        self.callback_func(data)
    
    # for uart protocal,  -------------------- TB Tested --------------------------
    def uart_decoder(self, data):
        # decode escape bytes
        result = b''
        
        i = 0
        while i < len(data):
            byte = data[i] # python gets the int type of single byte
            
            if byte != escape_byte:
                result += byte.to_bytes(1, 'big') # get the bytestring of this byte
                i += 1 # processed 1 byte for normal byte
                continue
            
            # byte == escape_byte, decode escaped byte
            byte_encoded = data[i + 1]
            byte_decoded = escape_byte ^ byte_encoded
            result += byte_decoded.to_bytes(1, 'big') # get the bytestring of this byte
            i += 2 # processed 2 byte for encoded byte
        # while loop done
        
        print("[Encoded]", data)
        print("[Decoded]", result)
        return result
    
    # for uart protocal, -------------------- TB Tested --------------------------
    def uart_encoder(self, data):
        # encode escape bytes
        result = b''
        for byte in data:
            if byte < escape_byte:
                result += byte.to_bytes(1, 'big') # get the bytestring of this byte
                continue
            
            # byte >= escape_byte, encode escaped byte
            byte_encoded = escape_byte ^ byte
            result += escape_byte.to_bytes(1, 'big') # get the bytestring of this byte
            result += byte_decoded.to_bytes(1, 'big') # get the bytestring of this byte
        # while loop done
        
        return result
    
    def sent_data(self, data):
        if self.serial_connection != None:
            data_encoded = uart_encoder(data)
            self.serial_connection.write(uart_start) # spcial byte marking start
            self.serial_connection.write(data_encoded)
            self.serial_connection.write(uart_end)   # spcial byte marking end
    
    def attack_callback(self, callback_func):
        self.callback_func = callback_func
        print(f"[Uart] Successfully attached callback function, {type(self.callback_func)}")
    
    # read the entire message base on protocal, -------------------- TB Finish --------------------------
    def uart_read_message(self):
        # read the entire message base on our uart escape byte protocal
        # TB Test
        data = b''
        while True:
            if self.serial_connection.in_waiting > 0:  # Check if there is data available to read
                byte = self.serial_connection.read() # Read and decode the data
                # print(byte, end="-")
                if byte == uart_start:
                    # start of message
                    data = b''
                    continue
                if byte == uart_end:
                    # found end of message sequence
                    break

                data += byte
        # end of while loop
        
        # decode the raw uart signals
        return self.uart_decoder(data)
    
    def uart_listening_thread(self):
        print("=== Enter uart listening thread === ")
        # listen to urat port
        # self.sent_data("[LOGOF]--".encode())
        
        while True:
            if self.serial_connection != None:
                try:
                    uart_message = self.uart_read_message()
                    self.uart_event_handler(uart_message)
                    print("> returend from uart handler")  # [Testing Log]
                    continue # successfuly read one message
                except serial.SerialException as e:
                    print(f"Serial communication error: {e}")
                    self.serial_connection = None # reset the connection
                except:
                    pass
            else:
                # No connection
                print("Uart trying to reconnect...")
                self.uart_connect()
                time.sleep(3)
    
    def run(self):
        print("Starting uart thread")
        self.uart_thread = threading.Thread(target=self.uart_listening_thread, args=(), daemon=True)
        self.uart_thread.start()
        print("Started uart thread")

import socket
import threading
import time
from datetime import datetime

class Socket_Manager():
    def __init__(self, server_listen_port, PACKET_SIZE):
        self.PACKET_SIZE = PACKET_SIZE
        self.server_listen_port = server_listen_port
        self.server_socket = None             # Listen for all socket connection
        self.server_listen_thread = None
        self.send_socket = None             # The Main communication Socket for python sending to C-API
        self.send_address = None
        self.callback_func = None
        
        self.initialize_socket()
    
    def initialize_socket(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', self.server_listen_port))
        self.server_socket.settimeout(None)  # accept_connectiondont timeout when waiting for response
                    
    def run(self):
        print("Starting socket thread")
        self.socket_thread = threading.Thread(target=self.server_listening_thread, args=(), daemon=True)
        self.socket_thread.start()
        print("Started socket thread")

                
    def connect_send_socket(self): # -------------------- TB Finish --------------------------
        self.server_socket.listen(1) # 1 space in queue is enough
        send_socket, send_address = self.server_socket.accept()
        
        # ====== inital extra handshake to confim it belong to our project =======
        # ====== verify is a send_socket (C_API's listen socket) =======
        # TB Finish
        # ====== end of confirmation
        self.send_socket = send_socket
        self.send_address = send_address
        print(f"Connected with send:{send_address}")

    
    def server_listening_thread(self):
        print("=== Enter socket (server) listening thread === ")
        # connect send_socket
        self.connect_send_socket()
        
        # listen to socket sonnection for C-API data/message request
        self.server_socket.listen(5)
        print(f"Listening on 'localhost':{self.server_listen_port} for C-API socket connection")
        while True:
            client_socket, address = self.server_socket.accept()
            print(f" - Request connection from C-API in {address} has been established.")
            
            request_handler_thread = threading.Thread(target=self.socket_handler, args=(client_socket,))
            request_handler_thread.start()


    def socket_handler(self, client_socket):
        print("Starting new C-API socket request thread")

        # read the request from C-API from socket
        data = client_socket.recv(self.PACKET_SIZE)
        # print("Received Request:", data.decode())

        # pass data to Net_Manager's function to handler and return the response
        response_bytes = self.callback_func(data)
        
        client_socket.send(response_bytes)
        client_socket.close()
    
    
    def attack_callback(self, callback_func):
        self.callback_func = callback_func
        print(f"[Socket] Successfully attached callback function, {type(self.callback_func)}")
        
        
    def send_data(self, data): # -------------------- TB Finish --------------------------
        print("sending data")
        if self.send_socket != None:
            # socket.sento(bytes, addr)
            self.send_socket.sendall(data)
        else:
            print("No socket connected")
            # implment attemps of reconnection
# Structure of Node
# No need for big change at the moment, will get final review and clean up when other stuff is confirmed working
# - need to remvoe the restriction of only servering GPS (not now)

from enum import Enum
from collections import deque
from datetime import datetime
import os

# Define the path for the new directory
log_folder = './history_log'

# Create the directory if it does not exist
if not os.path.exists(log_folder):
    os.makedirs(log_folder)
    print("Log Folder created:", log_folder)
else:
    print("Log Folder Verified exists:", log_folder)


def log_data_hist(data_type, data, time):
    file_path = log_folder + "/" + data_type + "_hist.txt"
    try:
        with open(file_path, 'a') as log_file:
            # Write text followed by a newline to the log file
            log_file.write(str(data) + ", " + str(time) + '\n')
    except:
        print("Can't log data to log_file", data_type, data)

class Node_Status(Enum):
    Active = 1
    Idol = 2
    Disconnect = 3
    
class Node:
    def __init__(self, name, address, uuid):
        self.name = name
        self.address = address
        self.uuid = uuid
        
        self.status = Node_Status.Active
        self.data_historys = {}
        
        self.data_historys["GPS"] = deque()            # (gps_data, time)
        self.data_historys["Load_Cell"] = deque()      # (load_data, time)
        self.data_historys["Robot_Request"] = deque()  # (request_count, time)
        self.last_contact_time = datetime.now()
        
#     def getData(self, data_type):
#         # ====== might not need this function anymore =========
#         # ====== since only cares about data's bytes=========
#         if data_type not in self.data_historys:
#             print(f"data type {data_type} not exist")
#             return None
        
#         return self.data_historys[data_type][-1][0]
        
    def getDataBytes(self, data_type):
        # ====== for GPS only for now =========
        # TB Finish - complte other data type
        # GPS - 6 byte - lontitude|latitude
        # ====== for GPS only for now =========
        
        # if data_type == "GPS":
            # gps_data = self.data_historys[data_type][-1][0]
            # data_byte = b''
            # data_byte += gps_data[0].to_bytes(3, byteorder='little')
            # data_byte += gps_data[1].to_bytes(3, byteorder='little')
            
            # return data_byte
        
        if data_type not in self.data_historys:
            print(f"data type {data_type} not exist")
            return b'F'

        return self.data_historys[data_type][-1][0]
    
    def storeData(self, data_type, data):
        if data_type not in self.data_historys:
            self.data_historys[data_type] = deque()
        
        time = datetime.now()
        self.data_historys[data_type].append((data, time))
        log_data_hist(data_type, data, time)
        
        # only kept latest 10 data in server
        if len(self.data_historys[data_type]) > 10:
            self.data_historys[data_type].popleft()
            
    def update_status(self, status):
        # need to implment how in detile the status affects Node's other function
        # TB Finish
        self.status = status
        
shared_node_list = []

class Network_Manager():
    def __init__(self):
        # Node list data struct
        # pull the node list from esp_module
        # create data structures
        global shared_node_list
        self.node_list = shared_node_list
        self.socket_sent = None
        self.uart_sent = None
        self.current_node = None
    
    def add_node(self, name, address, uuid):
        node = Node(name, address, uuid)
        self.node_list.append(node)
        print(f"node {address} added")
        return node
    
    def run_on_current_thread(self):
        print("Net Manager start running")
        while True:
            # print("Net Manager still running...")
            time.sleep(1)
            
    def attack_callback(self, socket_sent, uart_sent):
        self.socket_sent = socket_sent
        self.uart_sent = uart_sent

    # ============================= Socket Logics =================================
    # getNodeData needs the pre-defined data_type & length table, (not now),  -------------------- TB Finish --------------------------
    def getNodeData(self, data_type, node_addr):
        # <= data outgoing (single or patch)
        # S|data_type|data_length_byte|size_n|node_addr/index_0|data_0|...|node_addr/index_n|data_n
        # ^ success
        # F|Error_flag/Message
        data = b'S' + data_type.encode()
        
        if data_type != "GPS":
            print("only support GPS for testing, need define length of other data type in doc")
            return b'F-only support for GPS'

        # ============== need to be remake for correct data length ===================
        # TB Finish
        # ----- predefined data length for each type -------
        data_length_byte = 6 # 6 byte for GPS data
        data += data_length_byte.to_bytes(1, byteorder='little') # one byte for size, we won't have some data larger than 255 bytes
        # ----- predefined data length for each type -------
        
        
        # ------ untested get all node feature ---------------
        if node_addr == 255: # 0xFF => all nodes in same patch
            active_nodes = list(filter(lambda node: node.status == Node_Status.Active, self.node_list))
            size_n = len(active_nodes)
            data += size_n.to_bytes(1, byteorder='little') # one byte for size, we won't have more than 254 nodes
            for node in active_nodes:
                data += node.address.to_bytes(1, byteorder='little')
                data += node.getDataBytes(data_type)
        # ------ untested get all node feature ---------------

        elif node_addr != 255: # 0x## => single node
            node = list(filter(lambda node: node.address == node_addr, self.node_list))
            if len(node) == 0:
                error = "Node Not Found"
                data = b'F' + len(error).to_bytes(1, byteorder='little') + error.encode()
                return data
                
            node = node[0]
            data += node.address.to_bytes(1, byteorder='little')
            data += node.getDataBytes(data_type)

        # ============== need to be remake for correct data length ===================
        
        return data
        
    def callback_socket(self, data):
        print(f"[NetM] Triger callback from socket: {data}") # [Testing Log]
        op_code = data[0:5]
        payload = data[5:]
        try:
            op_code = op_code.decode('utf-8')
        except:
            print("[Socket] can't parse opcode", op_code)
            return b'F'
            
        if op_code == "[GET]":
            # [GET]|data_type|node_addr/index
            data_type = payload[0:3].decode('utf-8')
            node_addr = payload[3] # int.from_bytes(payload[3], byteorder='little')
            return self.getNodeData(data_type, node_addr)
            
        # for testing using "[ECHO]" testing code -----------------------
        if op_code == "ECHO-":
            message = data.decode('utf-8')
            message += " [Net] "
            print(" => pass message to uart")
            self.uart_sent(message.encode())
            return b'S'
        # testing code -----------------------
        #----------TB_review : response--------------
        if op_code == "[RES]":
            addr = data[5:7]
            payload = data[7:]
            message = addr +"<R>".encode() + payload
            print(" -> pass message to uart " + message.decode('utf-8'))
            #self.uart_sent(message.encode())
            #just for testing
            print("TEST: successfully receive response, ready to send: " )
            print(message)
            return b'S'
        # -------------------------------------------
        # faking uart request -----------------------
        op_code = data[0:3].decode('utf-8')
        if op_code == "<Q>":
            addr = data[3:5]
            payload = data[5:]
            lenth = 14
            new_data = addr + "<Q>".encode() +lenth.to_bytes(1, "little")  + payload
            print(new_data)
            self.callback_uart(new_data)
            return b'S'
        #



    # ============================= UART Logics =================================
    # updateNodeData needs the pre-defined data_type & length table, (not now),  -------------------- TB Finish --------------------------
    def updateNodeData(self, node_addr, msg_payload):
        print("updateNodeData from cmd:[D] on node:", node_addr)
        node = list(filter(lambda node: node.address == node_addr, self.node_list))
        if len(node) <= 0:
            node = self.add_node("Node",node_addr, None)
        else:
            node = node[0]
        
        #   size_n|data_type|data_length_byte|data|...|data_type|data_length_byte|data
        #    1   |   3     |     1          | n| ... (size of each segment in bytes)
        size = msg_payload[0]
        
        data_start = 1
        for n in range(size):
            data_type = msg_payload[data_start : data_start+3]
            data_len = msg_payload[data_start+3]
            
            print(f"data_type:{data_type}, data_len:{data_len}")
            
            try:
                data_type = data_type.decode('utf-8') # use string name if is a string name
            except:
                pass
            
            data = msg_payload[data_start+4: data_start+4+data_len]
        
            node.storeData(data_type, data)
            print(f"[Node] addr-{node_addr} added {data_type} data")
            data_start += 4 +  data_len
        
        print("done updating node:", node_addr)
        
    def callback_uart(self, data):
        print(f"[NetM] Triger callback from uart thread: {data}") # [Testing Log]
        node_addr = data[0:2]
        op_code = data[2:5]
        payload = data[5:]
        
        node_addr = int.from_bytes(node_addr, byteorder='little', signed=False)
        try:
            op_code = op_code.decode('utf-8')
        except:
            print("[Uart] can't parse opcode", op_code)
            return b'F'
        
        if op_code == "[D]":
            # Data update
            self.updateNodeData(node_addr, payload)
            
        
        # -------------- testing code -----------------------
        if "ECHO-".encode() == data[2:7]: # 1-2 is always added node addr
            message += " [Net] "
            print(" -> pass message to socket")  # [Testing Log]
            self.socket_sent(message.encode())
        # testing code -----------------------
        #--------TB_review : response----------------
        if op_code == "<Q>":
            socket_op_code = "[REQ]".encode()
            message = socket_op_code+node_addr.to_bytes(2, byteorder='little')+payload
            print(message)
            self.socket_sent(message)
        # -------------------------------------------
    
        print("> uart callback done")  # [Testing Log]


import time

PACKET_SIZE = 1024
server_socket_port = 5001
# port = '/dev/ttyUSB0' #'COM7'
port = 'COM5'
baud_rate = 115200

# Main function
def main():
    # Initialize The serial port & socket
    # Do locks sync for the shared vairable (serial_connection, socket)
    uart_manager = Uart_Task_Manager(port, baud_rate)
    socket_manager = Socket_Manager(server_socket_port, PACKET_SIZE)
    net_manager = Network_Manager()
    socket_manager.attack_callback(net_manager.callback_socket)
    uart_manager.attack_callback(net_manager.callback_uart)
    net_manager.attack_callback(socket_manager.send_data, uart_manager.sent_data)
    
    # Initialize uart_thread
    uart_manager.run()
    socket_manager.run()
    net_manager.run_on_current_thread()

if __name__ == "__main__":
    main()
    print("exit---------------")