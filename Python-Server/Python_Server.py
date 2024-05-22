import time
import os
from network_manager import Network_Manager
from uart_manager import Uart_Manager
from socket_manager import Socket_Manager
from node import Node

PACKET_SIZE = 1024
server_socket_port = 5001
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