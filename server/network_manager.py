import struct
import json
import asyncio
import random
from node import Node, Node_Status
from datetime import datetime
from message_opcodes import opcodes

shared_node_list = []

def get_data_len_by_id(data_id):
    with open('Data_Info.json', 'r') as file:
        data = json.load(file)
        
    for type_name, type_info in data.items():
        if type_info["ID"] == data_id:
            return type_info["Length"]
        
    print(f"[Error] Undefined data type data_id:{data_id}")
    return -1

class NetworkManager:
    def __init__(self):
        global shared_node_list
        self.node_list = shared_node_list
        self.current_node = None
        self.node_dict = {}
        self.socket_sent = None
        self.uart_sent = None
        self.web_sent = None
            
    def attach_callback(self, socket_sent, uart_sent, web_sent):
        self.socket_sent = socket_sent
        self.uart_sent = uart_sent
        self.web_sent = web_sent

    def update_dashboard(self, update):
        self.web_sent(update)

    def add_node(self, name: str, address: int, uuid: bytes) -> Node:
        node = Node(name, address, uuid)
        self.node_list.append(node)
        self.node_dict[address] = node
        print(f"Node-{address} added")
        
        update = {"event": "node_added", "node": node.__dict__}
        self.update_dashboard(update)
        return node
    
    def get_active_nodes(self):
        return list(filter(lambda node: node.status == Node_Status.Active, self.node_list))

    def update_node_data(self, node_addr: int, msg_payload: bytes):
        node = self.node_dict.get(node_addr)
        
        if node is None:
            node = self.add_node("Node", node_addr, b'')
        else:
            node = self.node_list[0]

        node.status = Node_Status.Active
        size = msg_payload[0]
        data_id_len = 1
        data_start = 1
        
        for n in range(size):
            data_ID = msg_payload[data_start : data_start + data_id_len]
            data_len = get_data_len_by_id(data_ID)
            
            if data_len == -1:
                print(f"Error updating node:{node_addr} payload'{msg_payload}'")
                return
            
            data = msg_payload[data_start + data_id_len: data_start + data_id_len + data_len]
            node.storeData(data_ID, data)
            data_start += data_id_len + data_len

        print("done updating node:", node_addr)
        update = {"event": "node_updated", "node": node.__dict__}
        self.update_dashboard(update)

    def callback_socket(self, data):
        if not data or len(data) < 5:
            print(f"Error: Received empty or malformed data: {data}")
            return b'F'
        
        command = data[0:5]
        payload = data[5:]
        print(f"\n[Socket-CB]: {command} {payload}")
        
        try:
            command = command.decode('utf-8')
        except UnicodeDecodeError:
            print("[Socket] can't parse command", command)
            return b'F'
        
        if command == "[GET]": # Get the data from the node
            node_addr = parseNodeAddr(payload[0:2])
            data_ID = payload[2:5].decode('utf-8')
            return self.get_node_data(data_ID, node_addr)
        
        if command == "ACT-C": # Get active nodes count
            count = len(self.get_active_nodes()) % 255
            return b'S' + str(count).encode('utf-8')
        
        if command == "NSTAT": # Get network status
            network_status = {
                "node_amount": len(self.node_list),
                "node_addr_list": list(map(lambda node: node.address, self.node_list)),
                "node_status_list": list(map(lambda node: 1 if node.status == Node_Status.Active else 0, self.node_list))
            }
            
            network_status_json = json.dumps(network_status)
            network_status_bytes = network_status_json.encode('utf-8')
            return b'S' + network_status_bytes

        if command == "RST-R":
            for node in self.node_list:
                node.status = Node_Status.Inactive
            self.uart_sent(data)
            self.update_dashboard({"event": "network_reset"})
            return b'S'
        
        return self.uart_sent(data)

    def callback_uart(self, data):
        if not data or len(data) < 3:
            print(f"Error: Received empty or malformed data: {data}")
            return b'F'
        
        node_addr_bytes = data[0:2]
        op_code = data[2:3]
        payload = data[3:]
        print(f"\n[UART-CB]: {node_addr_bytes} {op_code} {payload}")
        
        node_addr = parseNodeAddr(node_addr_bytes)
        
        if "Data" in opcodes and op_code == opcodes["Data"]:
            self.update_node_data(node_addr, payload)
            print(f"Node-{node_addr} updated")
            return b'S'
        
        if op_code == opcodes["Net Info"]:
            return b'S'
        
        if "Node Info" in opcodes and op_code == opcodes["Node Info"]:
            node_uuid = payload
            node_list = list(filter(lambda node: node.address == node_addr, self.node_list))
            
            if len(node_list) <= 0:
                node = self.add_node("Node", node_addr, node_uuid)
            else:
                node = node_list[0]
                node.uuid = node_uuid
                node.status = Node_Status.Active
                
            print(f"Node-{node_addr} connected")
            update = {"event": "node_connected", "node": node.__dict__}
            self.update_dashboard(update)
            return b'S'
        
        return self.socket_sent(data)

    def get_node_data(self, data_ID, node_addr: int):
        response = b'S' + data_ID.encode()
    
        if node_addr == 0:
            active_nodes = self.get_active_nodes()
            print(f"Active nodes: {active_nodes}")
            data_len = 0
        
            for node in active_nodes:
                hasData, data_len = node.getDataLength(data_ID)
                if hasData:
                    response += data_len.to_bytes(1, byteorder='little')
                    break
            
            size_n = 0
            total_data_bytes = b''
        
            for node in active_nodes:
                hasData, data = node.getDataBytes(data_ID)
            
                if hasData:
                    size_n += 1
                    total_data_bytes += encodeNodeAddr(node.address)
                    total_data_bytes += data
                
            response += size_n.to_bytes(1, byteorder='little')
            response += total_data_bytes
            return response
    
        elif node_addr != 0:
            node = self.node_dict.get(node_addr)
        
            if node is None:
                error = "Node Not Found"
                response = b'F' + len(error).to_bytes(1, byteorder='little') + error.encode()
                return response
        
            response += b'\x01'
            node = self.node_list[0]
            hasData, data = node.getDataBytes(data_ID)
        
            if not hasData:
                error = "Data Type Not Found"
                response = b'F' + len(error).to_bytes(1, byteorder='little') + error.encode()
                return response
        
            response += encodeNodeAddr(node.address)
            response += data
            return response

    async def simulate_updates(self):
        while True:
            # Directly call the get_node_data method to request data from the root module
            data_ID = "1" # Replace with the actual data ID you want to request
            node_addr = 0  # Root module address
            print(f"Simulating update for node-{node_addr}")
    
            # Call the get_node_data method
            response = self.get_node_data(data_ID, node_addr)
            print(response)
            
            # Change to json
            response_json = response.decode('utf-8')
            print(response_json)
            
            # Update the dashboard
            update = {"event": "data_update", "data": response_json}
            self.update_dashboard(update)
        
            await asyncio.sleep(2)


# Other Utility Functions
def encodeNodeAddr(node_addr: int) -> bytes:
    return struct.pack('!H', node_addr)

def parseNodeAddr(addr_bytes: bytes) -> int:
    return struct.unpack('!H', addr_bytes)[0]