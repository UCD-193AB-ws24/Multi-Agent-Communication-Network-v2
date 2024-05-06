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
            print("unable to connect to serial port", self.uart_port)
        
        
    def uart_event_handler(self, data):
        print(f"recived uart data: {data}")

        try:
            data_str = data.decode().strip()
            print(">", data_str)
        except:
            print(" - uart_data can't parse to string")

        # need uart protocal here =========================================================
        # TB Finish
        #         try:
        #             msg_type = data[:5].decode().strip()

        #             if (msg_type == "[CMD]"):
        #                 command_handler(data)
        #         except:
        #             print(" - Unable to retrive message_-type")
        
    
    # for uart protocal
    def uart_decoder(self):
        # TB Finish
        pass
    
    # for uart protocal
    def uart_encoder(self):
        # TB Finish
        pass
    
    def sent_data(self, data):
        print(f"[UART] send data {data}")
        self.serial_connection.write(data)
    
    def attack_callback(self, callback_func):
        self.callback_func = callback_func
        print(f"[Uart] Successfully attached callback function, {type(self.callback_func)}")
    
    def uart_listening_thread(self):
        print("=== Enter uart listening thread === ")
        # listen to urat port
        while True:
            if self.serial_connection != None:
                if self.serial_connection.in_waiting > 0:  # Check if there is data available to read
                    try:
                        data = self.serial_connection.readline()  # Read and decode the data
                        self.uart_event_handler(data)
                    except:
                        # fail to read line
                        pass
            else:
                # print("uart thread running")
                # time.sleep(0.1)
                # self.callback_func("hello from uart") # testing callback--------------------------------
                time.sleep(1)
    
    def run(self):
        print("Starting uart thread")
        self.uart_thread = threading.Thread(target=self.uart_listening_thread, args=(), daemon=True)
        self.uart_thread.start()
        print("Started uart thread")
        
import socket
import threading
import time
import select
from datetime import datetime

class Socket_Manager():
    def __init__(self, socket_port):
        self.PACKET_SIZE = 1024
        self.socket_port = socket_port
        self.socket_thread = None
        self.send_socket = None
        self.send_address = None
        self.read_socket = None
        self.read_address = None
        self.socket = None
        self.callback_func = None
        self.is_thread_alive = False
        
        self.initialize_socket()
    
    def initialize_socket(self):
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.bind(('localhost', self.socket_port))
        # tcp_socket.settimeout(None)  # dont timeout when waiting for response
        
        print("tcp port binded to port", self.socket_port) 
        self.socket = tcp_socket
        self.accept_connection()
    
    def accept_connection(self):
        self.socket.listen(2) # 2 space in queue is enough
        
        print(f"Listening on 'localhost':{self.socket_port} for connection")
        send_socket, send_address = self.socket.accept()
        read_socket, read_address = self.socket.accept()
        
        # ====== inital extra handshake to confim it belong to our project =======
        # TB Finish
        # ====== end of confirmation
        self.send_socket = send_socket
        self.send_address = send_address
        
        self.read_socket = read_socket
        self.read_address = read_address
        print(f"Connected with send:{send_address} read:{read_address}")
        return 0
    
    def send_data(self, data):
        if self.send_socket != None:
            # socket.sento(bytes, addr)
            self.send_socket.sendall(data)
        else:
            print("No socket connected")
    
    def socket_handler(self, data):
        print("recived data from socket:")
        # need to split the recived data into corresponding messages ---------------------------------------------
        # all the data sended from client in a short period of time will be read at once
        # define sepcial "END_OF_Message" pattern to split it
        # call task_handler after split message
        # TB Finish
        print(f"recived \"{data.decode('utf-8')}\"")
        try:
            message = data.decode('utf-8')
            if "[GET]" in message:
                self.callback_func(data)
        except:
            pass
        # ^^^ is just testing version of passing data to net manager function -- TB Finish
        
    def task_handler(self, message):
        # decode message, execute this task
        # TB Finish
        pass
    
    def attack_callback(self, callback_func):
        self.callback_func = callback_func
        print(f"[Socket] Successfully attached callback function, {type(self.callback_func)}")
        

    def socket_listening_thread(self):
        self.is_thread_alive = True
        print("=== Enter socket listening thread === ")
        # listen to socket
        while True:
            ready_to_read, _, _ = select.select([self.read_socket], [], [], 0)
            if ready_to_read == True:
                try:
                    data = self.read_socket.recv(PACKET_SIZE)
                    if(len(data) > 0):
                        self.socket_handler(data)
                    else:
                        time.sleep(0.1)               
                except socket.timeout:
                    print("timeout happened, no message back")
            else:
                print("need to reconnect")
                # try reconnect --------------------------------------------------------------------------
                # TB Finish
                time.sleep(1)
                # TB REVIEW
                self.is_thread_alive = False
                return 
                
    def run(self):
        print("Starting socket thread")
        self.socket_thread = threading.Thread(target=self.socket_listening_thread, args=(), daemon=True)
        self.socket_thread.start()
        print("Started socket thread")
        
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
        self.data_historys["Robot_Request"] = deque()  # (load_data, time)
        self.last_contact_time = datetime.now()
        
    def getData(self, data_type):
        if data_type not in self.data_historys:
            print(f"data type {data_type} not exist")
            return None
        
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
    def __init__(self,socket_manager, uart_manager):
        # Node list data struct
        # pull the node list from esp_module
        # create data structures
        global shared_node_list
        self.node_list = shared_node_list
        self.socket_sent = None
        self.uart_sent = None
        self.socket_manager = socket_manager
        self.uart_manager = uart_manager
    
    
    def add_nodes(self, name, address, uuid):
        node = Node(name, address, uuid)
        self.node_list.append(node)
    
    def run_on_current_thread(self):
        print("Net Manager start running")
        while True:
            # print("Net Manager still running...")
            
            #TB Review have a while loop that checks for disconnected threads and relaunches them
            if(self.socket_manager.is_thread_alive == False):
                print("Relaunching socket listening thread")
                if(self.socket_manager.accept_connection()):
                    self.socket_manager.run()
            time.sleep(1)
            
    def attack_callback(self, socket_sent, uart_sent):
        self.socket_sent = socket_sent
        self.uart_sent = uart_sent
        
    def callback_socket(self, data):
        print(f"[NetM] Triger callback from socket thread: {data}")
        # testing code -----------------------
        message = data.decode('utf-8')
        if "[GET]" in message:
            message += "[N]"
            print("  - pass message to uart")
            self.uart_sent(message.encode())
        # testing code -----------------------
    
    # for testing without uart
    def callback_socket_no_uart(self, data):
        print(f"[NetM] Triger callback from socket thread: {data}")
        # testing code -----------------------
        message = data.decode('utf-8')
        if "[GET]" in message:
            message = "[RES] python server received your message"
            print("  -from socket thread: send client message back")
            self.socket_sent(message.encode())
        
        
    def callback_uart(self, data):
        print(f"[NetM] Triger callback from uart thread: {data}")
        # testing code -----------------------
        message = data.decode('utf-8')
        if "[GET]" in message:
            message += "[N]"
            print("  - pass message to socket")
            self.socket_sent(message.encode())
        # testing code -----------------------
    

import time

PACKET_SIZE = 1024
socket_port = 5001
port = 'COM7'
baud_rate = 115200

# Main function
def main():
    # Initialize The serial port & socket
    # Do locks sync for the shared vairable (serial_connection, socket)
    uart_manager = Uart_Task_Manager(port, baud_rate)
    socket_manager = Socket_Manager(socket_port)
    # change the net_manager to contain uart_manager and socket_manager instance so it can relunch therad
    net_manager = Network_Manager(socket_manager, uart_manager)
    # socket_manager.attack_callback(net_manager.callback_socket)
    # just for testing client - python server communication
    socket_manager.attack_callback(net_manager.callback_socket_no_uart)
    
    uart_manager.attack_callback(net_manager.callback_uart)
    net_manager.attack_callback(socket_manager.send_data, uart_manager.sent_data)
    
    # Initialize uart_thread
    uart_manager.run()
    socket_manager.run()
    net_manager.run_on_current_thread()

if __name__ == "__main__":
    main()
    print("exit---------------")