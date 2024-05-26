from socket_api import Socket_Manager
from socket_api import getOpCodeNum, parseNodeAddr

# self_port = 6001
server_port = 5001
server_ip = "localhost"

def edge_robot_request_handler_example(node_addr):
    pass

def socket_message_callback_example(message_data: bytes):
    pass

def data_request_example(node_addr, data_type):
    pass

def main():
    server_addr = (server_ip, server_port)
    socket_api_manager = Socket_Manager(server_addr)
    socket_api_manager.run_socket_listen_thread(socket_message_callback_example)
    
    while True:
        # print("Programe still running...")
        time.sleep(1)

if __name__ == "__main__":
    main()