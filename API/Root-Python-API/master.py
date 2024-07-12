from socket_api import Socket_Manager
from socket_api import parseNodeAddr, craft_message_example
from field_test_benchmark import connect_N_node, RTT_tester, data_update_test
from opcode_subscribe import subscribe, unsubscribe, notify
from message_opcodes import opcodes
import time
# self_port = 6001
server_port = 5002
server_ip = "localhost"

    
def edge_robot_request_handler_example(node_addr):
    pass


def socket_message_callback_example(message_data: bytes):
    # print("[Socket]", end="=>")
    # print(f"Received message: {message_data}")
    
    node_addr_bytes = message_data[0:2]
    opcode = message_data[2:3]
    payload_bytes = message_data[3:]
    
    node_addr = parseNodeAddr(node_addr_bytes)

    # print("node_addr:",node_addr, ", opcode:", opcode, ", payload:", payload_bytes)

        
    # notify subscribers
    notify(opcode, message_data)
    # handler socket message
    if opcode == opcodes["Request"]:
        # request from edge
        pass


def data_request_example(socket_manager, node_addr, data_type):
    message = craft_message_example( "[GET]", node_addr, data_type)
    response = socket_manager.socket_sent(message)
    if response[0:1] == b'F':
        print("Failed to get data")
        return

# def full_restart_root(socket_manager):
#     message = craft_message_example( "RST-R", 0, b'')
#     response = socket_manager.socket_sent(message)
#     if response[0:1] == b'F':
#         print("Failed to get data")
#         return

def node_check(socket_manager, desinated_node):
    message_str = "T" + "I" + "0"
    message_bytes = message_str.encode()

    for node in desinated_node:
        message = craft_message_example( "SEND-", node, message_bytes)
        response = socket_manager.socket_sent(message)
        time.sleep(1)

    time.sleep(20)

def main():
    server_addr = (server_ip, server_port)
    socket_api = Socket_Manager(server_addr, socket_message_callback_example)
    socket_api.run_socket_listen_thread()
    # full_restart_root(socket_api)
    time.sleep(3)

    # desinated_node = [5, 6, 7, 8, 9, 10 ,11, 12, 13, 14] #, 7, 8, 9]
    
    desinated_node = [5, 6, 9, 12, 13, 14] #, 7, 8, 9]
    node_amount = len(desinated_node) # control how many node testing

    # node_check(socket_api, desinated_node)

    # connect_N_node(socket_api, node_amount, desinated_node)
    
    # data_update_test(socket_api, node_amount, 20, 1, desinated_node)

    # check node online
    desinated_node = [10]
    node_amount = len(desinated_node) # control how many node testing
    RTT_test_parameters = [] # (data_size, send_rate Hz, duration)
    RTT_test_parameters.append((10, 1, 20))
    # RTT_test_parameters.append((20, 0.5, 10))
    # RTT_test_parameters.append((40, 0.5, 60))

    print("testing:", desinated_node)
    for i in range(len(RTT_test_parameters)):
        data_size, send_rate, duration = RTT_test_parameters[i]
        RTT_tester(socket_api, node_amount, data_size, send_rate, duration, desinated_node)

    
    # data_update_test(socket_api, node_amount, 20, 1, desinated_node)
    # connect_N_node(socket_api, node_amount)
    
    print("All Test Finished, running [GET] Command")
    print("Programe still running...")
    time.sleep(10)
    while True:
        # print("Programe still running...")
        data_request_example(socket_api, 5, b'\x00')
        time.sleep(10)

if __name__ == "__main__":
    main()