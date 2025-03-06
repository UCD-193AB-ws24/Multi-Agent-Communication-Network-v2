import os
from network_manager import Network_Manager
from uart_manager import Uart_Manager
from socket_manager import Socket_Manager

PACKET_SIZE = 1024
SERVER_SOCKET_PORT = 5001
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200

# Define the path for the new directory
log_folder = './history_log'

# Create the directory if it does not exist
if not os.path.exists(log_folder):
    os.makedirs(log_folder)
    print("Log Folder created:", log_folder)
else:
    print("Log Folder Verified exists:", log_folder)

def main():
    # Initialize the serial port & socket
    uart_manager = Uart_Manager(SERIAL_PORT, BAUD_RATE)
    socket_manager = Socket_Manager(SERVER_SOCKET_PORT, PACKET_SIZE)
    net_manager = Network_Manager()
    
    socket_manager.attach_callback(net_manager.callback_socket)
    uart_manager.attach_callback(net_manager.callback_uart)
    net_manager.attach_callback(socket_manager.send_data, uart_manager.sent_data)

    uart_manager.run()
    socket_manager.run()
    net_manager.run_on_current_thread()

if __name__ == "__main__":
    main()
    print("Server has shut down.")
