from socket_api import Socket_Manager
from socket_api import getOpCodeNum, parseNodeAddr

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
    pass

def data_request_example(node_addr, data_type):
    pass

def main():
    server_addr = (server_ip, server_port)
    socket_api = Socket_Manager(server_addr)
    socket_api.run_socket_listen_thread(socket_message_callback_example)
    
    while True:
        # print("Programe still running...")
        time.sleep(1)

if __name__ == "__main__":
    main()