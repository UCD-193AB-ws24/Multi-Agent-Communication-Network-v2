import time
import os
from network_manager import Network_Manager
from uart_manager import Uart_Manager
from socket_manager import Socket_Manager
from web_socket_proxy_server import Web_Socket_Manager

PACKET_SIZE = 1024
server_socket_port = 5002
proxy_server_port = 7654
# port = '/dev/ttyUSB0' #'COM7'
port = '/dev/ttyUSB0'
baud_rate = 115200

# Define the path for the new directory
log_folder = './history_log'

# Create the directory if it does not exist
if not os.path.exists(log_folder):
    os.makedirs(log_folder)
    print("Log Folder created:", log_folder)
else:
    print("Log Folder Verified exists:", log_folder)


# Main function
def main():
    # Initialize The serial port & socket
    # Do locks sync for the shared vairable (serial_connection, socket)
    uart_manager = Uart_Manager(port, baud_rate)
    socket_manager = Socket_Manager(server_socket_port, PACKET_SIZE)
    net_manager = Network_Manager()
    web_manager = Web_Socket_Manager(port=proxy_server_port)
    socket_manager.attach_callback(net_manager.callback_socket)
    uart_manager.attach_callback(net_manager.callback_uart)
    net_manager.attach_callback(socket_manager.send_data, uart_manager.sent_data, web_manager.send_to_web)
    
    # Initialize uart_thread
    uart_manager.run()
    socket_manager.run()
    web_manager.run()

    print("=== Sending ====== ")
    data = {
        "type": "networkStatus",
        "status": "nodeStatus",
        "nodes": [
            {"name": "Node-0", "status": "normal"},
            {"name": "Node-1", "status": "normal"}
        ]
    }
    web_manager.send_to_web(data)
    print("=== Sending ====== ")
    
    net_manager.run_on_current_thread()

if __name__ == "__main__":
    main()
    print("exit---------------")
