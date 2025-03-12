import struct
import json
import asyncio
from node import Node, Node_Status
from datetime import datetime
from message_opcodes import opcodes
import random

def get_data_len_by_id(data_id):
    with open('Data_Info.json', 'r') as file:
        data = json.load(file)
        
    for type_name, type_info in data.items():
        if type_info["ID"] == data_id:
            return type_info["Length"]
        
    print(f"[Error] Undefined data type data_id:{data_id}")
    return -1

def encodeNodeAddr(node_addr: int) -> bytes:
    return struct.pack('!H', node_addr)

def parseNodeAddr(addr_bytes: bytes) -> int:
    return struct.unpack('!H', addr_bytes)[0]

class NetworkManager:
    def __init__(self):
        self.node_list = []
        self.node_dict = {}
        self.send_socket = None
        self.send_uart = None
        self.send_web = None
            
    def attach_callback(self, send_socket, send_uart, send_web):
        self.send_socket = send_socket
        self.send_uart = send_uart
        self.send_web = send_web

    def update_dashboard(self, update):
        self.send_web(update)

    def add_node(self, name: str, address: int, uuid: bytes) -> Node:
        node = Node(name, address, uuid)
        self.node_list.append(node)
        self.node_dict[address] = node
        print(f"{datetime.now()} - Node-{address} with UUID:{uuid} added")
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

        print(f"{datetime.now()} - Node-{node_addr} updated")
    
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
    
    def handle_network_info(self, payload):
        batch_size = payload[0]
        offset = 1
        for _ in range(batch_size):
            node_addr = struct.unpack('!H', payload[offset:offset + 2])[0]
            offset += 2
            node_uuid = payload[offset:offset + 16]
            offset += 16
            
            if node_addr in self.node_dict:
                print(f"Node-{node_addr} already exists")
            else:
                self.add_node("Node", node_addr, node_uuid)
    
    # TODO: Handle Direct Forwarding Info will update the node list with the direct forwarding paths
    # Update node list with another attribute for their direct forwarding paths
    def handle_direct_forwarding_info(self, payload):
        # Temporarily print the payload
        # Decoded date: b'\x04\x02\x12\x34\x56\x78\x9A\xBC\xDE\xF0'
        # Number of paths: 2
        # Path 0: 0x1234 -> 0x5678
        # Path 1: 0x9ABC -> 0xDEF0
        if len(payload) < 2:
            print("Invalid data length")
            return

        opcode = payload[0]
        num_paths = payload[1]

        if opcode != 0x04:
            print("Invalid opcode")
            return

        print(f"Number of paths: {num_paths}")

        index = 2
        for i in range(num_paths):
            if index + 4 > len(payload):
                print("Invalid data length for paths")
                return

        path_origin = int.from_bytes(payload[index:index+2], 'big')
        path_target = int.from_bytes(payload[index+2:index+4], 'big')
        index += 4

        print(f"Path {i}: 0x{path_origin:04X} -> 0x{path_target:04X}")

        return b'F' + "Not Implemented".encode()

    def callback_socket(self, data):
        if not data or len(data) < 5:
            print(f"Error: Received empty or malformed data: {data}")
            return b'F'
        
        command = data[0:5]
        payload = data[5:]
        print(f"{datetime.now()} - Received Socket data: {data}")
        
        try:
            command = command.decode('utf-8')
        except UnicodeDecodeError:
            print("[Socket] can't parse command", command)
            return b'F'
        
        if command == "[GET]":
            node_addr = parseNodeAddr(payload[0:2])
            data_ID = payload[2:5].decode('utf-8')
            return self.get_node_data(data_ID, node_addr)
        elif command == "ACT-C":
            count = len(self.get_active_nodes()) % 255
            return b'S' + str(count).encode('utf-8')
        elif command == "NINFO":
            self.send_uart(b'NINFO')
            network_status = {
                "node_amount": len(self.node_list),
                "node_addr_list": list(map(lambda node: node.address, self.node_list)),
                "node_status_list": list(map(lambda node: 1 if node.status == Node_Status.Active else 0, self.node_list))
            }
            network_status_json = json.dumps(network_status)
            network_status_bytes = network_status_json.encode('utf-8')
            return b'S' + network_status_bytes
        elif command == "RST-R":
            for node in self.node_list:
                node.status = Node_Status.Disconnect
            self.send_uart(data)
            return b'S'
        elif command == "SEND-" or command == "BCAST":
            self.send_uart(data)
            return b'S'
        elif command == "DFINFO":
            self.send_uart(b'DFINFO')
            return b'S'

        return b'F' + "Unknown Command".encode()

    def callback_uart(self, data):
        if not data or len(data) < 3:
            print(f"Error: Received empty or malformed data: {data}")
            return b'F'
        
        node_addr_bytes = data[0:2]
        op_code = data[2:3]
        payload = data[3:]
        print(f"{datetime.now()} - Received UART data: {data}")
        
        node_addr = parseNodeAddr(node_addr_bytes)
        
        if "Data" in opcodes and op_code == opcodes["Data"]:
            self.update_node_data(node_addr, payload)
            update = {"event": "node_updated", "node": self.node_dict[node_addr].__dict__}
        elif "Net Info" in opcodes and op_code == opcodes["Net Info"]:
            self.handle_network_info(payload)
            update = {"event": "network info", "node": self.node_dict[node_addr].__dict__}
        elif "Node Info" in opcodes and op_code == opcodes["Node Info"]:
            node_uuid = payload
            node_list = list(filter(lambda node: node.address == node_addr, self.node_list))
            if len(node_list) <= 0:
                node = self.add_node("Node", node_addr, node_uuid)
            else:
                node = node_list[0]
                node.uuid = node_uuid
                node.status = Node_Status.Active
            update = {"event": "node_connected", "node": node.__dict__}
        elif "DF Info" in opcodes and op_code == opcodes["DF Info"]:
            self.handle_direct_forwarding_info(payload)
        else:
            return b'F' + "Unknown Opcode".encode()

        self.update_dashboard(update)
        
        return b'S'
    
    async def simulate_updates(self):
        while True:
            # Generate random latitude and longitude within specified range
            latitude = round(random.uniform(38.539466, 38.543397), 6)
            longitude = round(random.uniform(-121.777816, -121.769394), 6)

            # Generate random update data
            update = {
                "event": random.choice(["node_added", "node_updated", "node_connected"]),
                "node": {
                    "name": f"Node{random.randint(1, 10)}",
                    "longitude": longitude,
                    "latitude": latitude,
                    "uuid": f"uuid-{random.randint(1, 100)}",
                    "status": random.choice(["Active", "Inactive"]),
                    "data": {f"data{random.randint(1, 5)}": random.randint(1, 100)}
                }
            }
            self.update_dashboard(update)
            await asyncio.sleep(2)