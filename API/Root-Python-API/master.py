from socket_api import Socket_Manager
from socket_api import parseNodeAddr, craft_message_example
from field_test_benchmark import connect_N_node
from opcode_subscribe import subscribe, unsubscribe, notify
import time
# self_port = 6001
server_port = 5001
server_ip = "localhost"

    
def edge_robot_request_handler_example(node_addr):
    pass


def socket_message_callback_example(message_data: bytes):
    print("[Socket]", end="=>")
    print(f"Received message: {message_data}")
    
    node_addr_bytes = message_data[0:2]
    opcode_bytes = message_data[2:5]
    payload_bytes = message_data[5:]
    
    node_addr = parseNodeAddr(node_addr_bytes)
    opcode = "---"
    try:
        opcode = opcode_bytes.decode('utf-8')
    except:
        print("Can't parse opcode", opcode)
        return

    print("node_addr:",node_addr, ", opcode:", opcode, ", payload:", payload_bytes)

        
    # notify subscribers
    notify(opcode, message_data)
    # handler socket message
    if opcode == "[REQ]":
        # request from edge
        pass


def data_request_example(socket_manager, node_addr, data_type):
    message = craft_message_example( "[GET]", node_addr, data_type.encode())
    response = socket_manager.socket_sent(message)
    if response[0:1] == b'F':
        print("Failed to get data")
        return

def full_restart_root(socket_manager):
    message = craft_message_example( "RST-R", 0, b'')
    response = socket_manager.socket_sent(message)
    if response[0:1] == b'F':
        print("Failed to get data")
        return

def main():
    server_addr = (server_ip, server_port)
    socket_api = Socket_Manager(server_addr, socket_message_callback_example)
    socket_api.run_socket_listen_thread()
    full_restart_root(socket_api)
    
    time.sleep(1)

    connect_N_node(socket_api, 1)
    
    
    print("Programe still running...")
    time.sleep(10)
    while True:
        # print("Programe still running...")
        data_request_example(socket_api,6, "GPS")
        time.sleep(10)

if __name__ == "__main__":
    main()