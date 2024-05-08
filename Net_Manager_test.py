import serial
import threading
import time

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
            #comment out print
            return
            # print("unable to connect to serial port", self.uart_port)
        
        
    def uart_event_handler(self, data):
        # print("recived uart data:")
        self.callback_func(data)
        
        # try:
        #     data_str = data.decode().strip()
        #     print(">", data_str)
        # except:
        #     print(" - uart_data can't parse to string")
        # need uart protocal here =========================================================
        # TB Finish
        # try:
        #     msg_type = data[:5].decode().strip()

        #     if (msg_type == "[CMD]"):
        #         command_handler(data)
        # except:
        #     print(" - Unable to retrive message_-type")
    
    # for uart protocal
    def uart_decoder(self):
        # TB Finish
        pass
    
    # for uart protocal
    def uart_encoder(self):
        # TB Finish
        pass
    
    def sent_data(self, data):
        self.serial_connection.write(data)
    
    def attack_callback(self, callback_func):
        self.callback_func = callback_func
        print(f"[Uart] Successfully attached callback function, {type(self.callback_func)}")
    
    def uart_listening_thread(self):
        print("=== Enter uart listening thread === ")
        # listen to urat port
        
        # ------------------------------ temparary removal for testing with only socket client and python server
        # self.sent_data("[LOGOF]--".encode())
        #----------------------------------
        while True:
            if self.serial_connection != None:
                try:
                    if self.serial_connection.in_waiting > 0:  # Check if there is data available to read
                        data = self.serial_connection.readline()  # Read and decode the data
                        self.uart_event_handler(data)
                except serial.SerialException as e:
                    print(f"Serial communication error: {e}")
                    # self.serial_connection = None
                except:
                    # fail to read line
                    pass
            else:
                # print("uart thread running")
                # time.sleep(0.1)
                # self.callback_func("hello from uart") # testing callback--------------------------------

                # print("try to reconnect") # comment out for testing client-server without uart
                self.uart_connect()
                time.sleep(1)
    
    def run(self):
        print("Starting uart thread")
        self.uart_thread = threading.Thread(target=self.uart_listening_thread, args=(), daemon=True)
        self.uart_thread.start()
        print("Started uart thread")
        
import socket
import threading
import time
from datetime import datetime

# server_socket is the socket that listen to client's sent request, 1 to multiple client's sent socket
# send_socket is the persistent socket that connect to the client's listen socket
#
class Socket_Manager():
    def __init__(self, server_listen_port, PACKET_SIZE):
        self.PACKET_SIZE = PACKET_SIZE
        self.server_listen_port = server_listen_port
        self.server_socket = None
        self.server_listen_thread = None
        self.send_socket = None
        self.send_address = None
        self.callback_func = None
        self.disconnect = True
        
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

                
    def connect_send_socket(self):
        self.server_socket.listen(1) # 1 space in queue is enough
        # send_socket, send_address = self.server_socket.accept()
        
        # ====== inital extra handshake to confim it belong to our project =======
        # ====== verify is a send_socket (C_API's listen socket) =======
        # TB Finish
        # TB Review
        while (self.disconnect == True):
            send_socket, send_address = self.server_socket.accept()
            data = send_socket.recv(self.PACKET_SIZE)
            print("data: ", data)
            if data != b'[syn]\x00':
                send_socket.send(b'[err]-listen_socket_disconnected')
                send_socket.close()
            else:
                print("connected to listen")
                send_socket.send(b'[ack]\x00')
                self.disconnect = False
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
            # reconnect send socket if disconnect TB Review
            if(self.disconnect == True):
                print("---------------------------reconnnecting------------------------------")
                self.connect_send_socket()
            
            client_socket, address = self.server_socket.accept()
            print(f" - Request connection from C-API in {address} has been established.")
            # print(f" - client socket: {client_socket}")
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
        
    # def task_handler(self, message):
    #     # decode message, execute this task
    #     # TB Finish
    #     pass
    
    def attack_callback(self, callback_func):
        self.callback_func = callback_func
        print(f"[Socket] Successfully attached callback function, {type(self.callback_func)}")
        
    
# ---------------------- fixing ----------------------------   
# detect if client listening is open here 
# TB Review      
    def send_data(self, data):
        time.sleep(4)
        if self.send_socket != None:
            print("send_data called")
            try:
                self.send_socket.sendall(data)
            except socket.error as e:
                err_no = e.errno
                error_str = e.strerror
                if(err_no == 32 or err_no == 104 or err_no == 111):
                    print("Client socket disconnected")
                    self.send_socket.close()
                    self.disconnect = True
                if err_no == 110:
                    print("Connection timeout")
        else:
            print("No socket connected")
            
from enum import Enum

def log_data_hist(data_type, data, time):
    try:
        with open(data_type + "_hist.txt", 'a') as log_file:
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
        
    def getData(self, data_type):
        # ====== might not need this function anymore =========
        # ====== since only cares about data's bytes=========
        if data_type not in self.data_historys:
            print(f"data type {data_type} not exist")
            return None
        
        return self.data_historys[data_type][-1][0]
        
    def getDataBytes(self, data_type):
        # ====== for GPS only for now =========
        # TB Finish - complte other data type
        # GPS - 6 byte - lontitude|latitude
        # ====== for GPS only for now =========
        
        if data_type == "GPS":
            gps_data = self.data_historys[data_type][-1][0]
            data_byte = b''
            data_byte += gps_data[0].to_bytes(3, byteorder='big')
            data_byte += gps_data[1].to_bytes(3, byteorder='big')
            
            return data_byte
            
        print(f"other type {data_type} not yet supported")
        return b'FFFFFF'
    
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
    
    def add_nodes(self, name, address, uuid):
        node = Node(name, address, uuid)
        self.node_list.append(node)
    
    def run_on_current_thread(self):
        print("Net Manager start running")
        while True:
            # print("Net Manager still running...")
            time.sleep(1)
            
    def attack_callback(self, socket_sent, uart_sent):
        self.socket_sent = socket_sent
        self.uart_sent = uart_sent

    # ============================= Socket Logics =================================
    def getNodeData(self, data_type, node_addr):
        # <= data outgoing (single or patch)
        # S|data_type|data_length_byte|size_n|node_addr/index_0|data_0|...|node_addr/index_n|data_n
        # ^ success
        # F|Error_flag/Message
        data = b'S' + data_type.encode()

        # ----- predefined data length for each type -------
        data_length_byte = 6 # 6 byte for GPS data
        # TB Finish
        data += data_length_byte.to_bytes(1, byteorder='big') # one byte for size, we won't have some data larger than 255 bytes
        # ----- predefined data length for each type -------
        
        if node_addr == 255: # 0xFF => all nodes in same patch
            active_nodes = list(filter(lambda node: node.status == Node_Status.Active, self.node_list))
            size_n = len(active_nodes)
            data += size_n.to_bytes(1, byteorder='big') # one byte for size, we won't have more than 254 nodes
            for node in active_nodes:
                data += node.address.to_bytes(1, byteorder='big')
                data += node.getDataBytes(data_type)

        elif node_addr != 255: # 0x## => single node
            node = list(filter(lambda node: node.address == node_addr, self.node_list))
            if len(node) == 0:
                error = "Node Not Found"
                data = b'F' + len(error).to_bytes(1, byteorder='big') + error.encode()
                return data
                
            node = node[0]
            data += node.address.to_bytes(1, byteorder='big')
            data += node.getDataBytes(data_type)

        return data
        
        
    def callback_socket(self, data):
        print(f"[NetM] Triger callback from socket thread: {data}")
        op_code = data[0:5]
        payload =  data[5:]
        try:
            op_code = op_code.decode('utf-8')
        except:
            print("can't parse opcode")
            return b'F'
            
        # if op_code == "[GET]":
        #     # [GET]|data_type|node_addr/index
        #     data_type = payload[0:3].decode('utf-8')
        #     node_addr = int.from_bytes(payload[3], byteorder='big')
        #     return self.getNodeData(data_type, node_addr)
            
        # for testing using "[GET]" testing code -----------------------
        if op_code == "[GET]":
            message = data.decode('utf-8')
            message += "[N]"
            # ---------------testing without UART-----------
            print(" => callback: from server to client")
            message = "[REQ] server response to GET"
            self.socket_sent(message.encode())
            # ---------------testing without UART-----------
            
            # print(" => pass message to uart")
            # self.uart_sent(message.encode())
            return b'Socket'
        # testing code -----------------------



    # ============================= UART Logics =================================
        
    def callback_uart(self, data):
        print(f"[NetM] Triger callback from uart thread: {data}")
        # testing code -----------------------
        message = data.decode('utf-8')
        if "[GET]" in message:
            message += "[N]"
            print(" -> pass message to socket")
            self.socket_sent(message.encode())
        # testing code -----------------------
    
import time

PACKET_SIZE = 1024
server_socket_port = 5001
port = '/dev/ttyUSB0' #'COM7'
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