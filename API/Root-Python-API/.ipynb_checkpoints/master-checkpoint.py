from socket_api import Socket_Manager
from socket_api import parseNodeAddr, craft_message_example
from field_test_benchmark import Test_0_connect_10_node
import time
# self_port = 6001
server_port = 5001
server_ip = "localhost"

socket_event_subscriber = {}

def subscribe(opcode, callback):
    if opcode not in socket_event_subscriber:
        socket_event_subscriber[opcode] = []
        
    socket_event_subscriber[opcode].append(callback)
    
def unsubscribe(opcode, callback):
    if opcode not in socket_event_subscriber:
        print(f"opcode: \'{opcde}\' has no subscriber")
        return
    
    if callback not in socket_event_subscriber[opcode]:
        print(f"opcode: \'{opcde}\' has no subscriber from this callback")
        return
    
    socket_event_subscriber[opcode].remove(callback)
    
def notify(opcode, data):
    if opcode in socket_event_subscriber:
        for callback in socket_event_subscriber[opcode]:
            try:
                callback(data)
            except Exception as e:
                print(f"Error occurred when invoke callback for \'{opcode}\'")
                print(f"Error: {e}")
                unsubscribe(opcode, callback)
    
def edge_robot_request_handler_example(node_addr):
    pass


def socket_message_callback_example(message_data: bytes):
    print("callback called")
    print(f"Received message: {message_data}")
    
    node_addr_bytes = message_data[0:2]
    opcode_bytes = message_data[2:5]
    payload_bytes = message_data[5:]
    
    node_addr = parseNodeAddr(node_addr_bytes)
    opcode = "---"
    try:
        opcode = opcode_bytes.decode('utf-8')
    except:
        print("Can't parse opcode", op_code)
        return
        
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


def main():
    server_addr = (server_ip, server_port)
    socket_api = Socket_Manager(server_addr, socket_message_callback_example)
    socket_api.run_socket_listen_thread()

    Test_0_connect_10_node(socket_api)
    
    
    print("Programe still running...")
    time.sleep(10)
    while True:
        # print("Programe still running...")
        data_request_example(socket_api,5, "GPS")
        time.sleep(2)

if __name__ == "__main__":
    main()