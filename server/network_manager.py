import struct
import json
from node import Node, Node_Status
from message_opcodes import OPCODES

def get_data_len_by_id(data_id):
    with open('Data_Info.json', 'r') as file:
        data = json.load(file)
    data_id_int = int.from_bytes(data_id, byteorder='big') if isinstance(data_id, bytes) else data_id
    for type_name, type_info in data.items():
        if type_info["ID"] == data_id_int:
            return type_info["Length"]
    print(f"[ERROR][] Undefined data type data_id:{data_id}")
    return -1

def encodeNodeAddr(node_addr: int) -> bytes:
    return struct.pack('!H', node_addr)

def parseNodeAddr(addr_bytes: bytes) -> int:
    return struct.unpack('!H', addr_bytes)[0]

class NetworkManager:
    def __init__(self):
        self.node_list = []
        self.node_dict = {}
        self.df = []
        self.send_socket = None
        self.send_uart = None
        self.send_web = None

    def log(self, level, message):
        print(f"[NETWORK][{level}]  - {message}")

    def attach_callback(self, send_socket, send_uart, send_web):
        self.send_socket = send_socket
        self.send_uart = send_uart
        self.send_web = send_web
        
    def get_active_nodes(self):
        return [node for node in self.node_list if node.status == Node_Status.Active]

    def get_node_data(self, data_ID, node_addr: int):
        response = b'S' + data_ID.encode()

        if node_addr == 0:
            active_nodes = self.get_active_nodes()
            self.log("INFO", f"Gathering {data_ID} from all active nodes")
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

        node = self.node_dict.get(node_addr)
        if node is None:
            return b'F' + b"Node Not Found"

        response += b'\x01'
        hasData, data = node.getDataBytes(data_ID)
        if not hasData:
            return b'F' + b"Data Type Not Found"

        response += encodeNodeAddr(node.address)
        response += data
        return response

    def add_node(self, name, address, uuid_bytes):
        if address in self.node_dict:
            self.log("INFO", f"Node-{address:04X} already exists, skipping re-add")
            return self.node_dict[address]

        node = Node(name=name, address=address, uuid=uuid_bytes)
        self.node_dict[address] = node
        self.node_list.append(node)
        self.log("INFO", f"Node-{address:04X} with UUID: {uuid_bytes.hex()} added")
        return node

    
    def update_node_data(self, node_addr, payload):
        if not payload or len(payload) < 1:
            self.log("ERROR", "Empty or malformed data payload")
            return

        data_id_byte = payload[0:1]
        data_id = int.from_bytes(data_id_byte, 'big')

        self.log("DEBUG", f"Raw payload: {payload}")
        self.log("DEBUG", f"data_id (byte): {data_id_byte}, int: {data_id}")

        data_len = get_data_len_by_id(data_id_byte)
        if data_len is None or len(payload) < 1 + data_len:
            self.log("ERROR", f"Invalid data type for node {node_addr}, payload: {payload}")
            return

        value_bytes = payload[1:1 + data_len]

        if node_addr not in self.node_dict:
            self.log("ERROR", f"Data received for unknown node {node_addr}")
            return

        node = self.node_dict[node_addr]

        # Handle GPS (data_id == 5)
        if data_id == 5 and data_len == 16:
            lat = struct.unpack('<d', value_bytes[0:8])[0]
            lon = struct.unpack('<d', value_bytes[8:16])[0]
            node.gps = (lat, lon)
            self.log("DATA", f"Node-0x{node_addr:04X} GPS updated to (lat: {lat:.6f}, lon: {lon:.6f})")
        else:
            self.log("ERROR", f"Unsupported data_id {data_id} or invalid length {data_len}")

        self.log("DATA", f"Node-0x{node_addr:04X} data updated")
    
    def update_node_gps(self, node_addr, payload):
        if len(payload) != 16:
            self.log("ERROR", f"Expected 16 bytes for GPS, got {len(payload)}")
            return

        lat = struct.unpack('<d', payload[0:8])[0]
        lon = struct.unpack('<d', payload[8:16])[0]

        if node_addr not in self.node_dict:
            self.log("ERROR", f"GPS received for unknown node {node_addr}")
            return

        node = self.node_dict[node_addr]
        node.gps = (lat, lon)
        self.log("DATA", f"Node-0x{node_addr:04X} GPS updated to (lat: {lat:.6f}, lon: {lon:.6f})")

    def handle_network_info(self, payload):
        batch_size = payload[0]
        offset = 1
        seen_addrs = set()

        for _ in range(batch_size):
            node_addr = struct.unpack('!H', payload[offset:offset + 2])[0]
            offset += 2
            node_uuid = payload[offset:offset + 16]
            offset += 16
            
            if node_addr in seen_addrs:
                continue
            
            seen_addrs.add(node_addr)

            if node_addr not in self.node_dict:
                node = self.add_node("Node", node_addr, node_uuid)
                node.status = Node_Status.Active
                node.missed_updates = 0
                self.print_node_info(node)
            else:
                node = self.node_dict[node_addr]
                node.status = Node_Status.Active
                node.missed_updates = 0
                self.log("INFO", f"Node-{node_addr:04X} seen again, marked Active")

        for addr, node in self.node_dict.items():
            if addr not in seen_addrs:
                if node.status == Node_Status.Active:
                    node.status = Node_Status.Idle
                    node.missed_updates = 1
                    self.log("WARNING", f"Node-{addr:04X} not seen, marked Idle")
                elif node.status == Node_Status.Idle:
                    node.missed_updates += 1
                    if node.missed_updates >= 2:
                        node.status = Node_Status.Disconnect
                        self.log("ERROR", f"Node-{addr:04X} missed 2 updates, marked Disconnected")
                    else:
                        self.log("WARNING", f"Node-{addr:04X} still Idle, missed {node.missed_updates} updates")
                elif node.status == Node_Status.Disconnect:
                    self.log("INFO", f"Node-{addr:04X} still Disconnected")
    
    def handle_direct_forwarding_info(self, payload):
        if len(payload) < 1:
            self.log("ERROR", "Invalid DFGET payload length")
            return b'F'

        num_paths = payload[0]
        self.log("DFGET", f"{num_paths} direct forwarding paths received")

        self.df.clear()
        index = 1

        for i in range(num_paths):
            if index + 4 > len(payload):
                self.log("ERROR", "Truncated forwarding path entry")
                return b'F'

            path_origin = int.from_bytes(payload[index:index+2], 'big')
            path_target = int.from_bytes(payload[index+2:index+4], 'big')
            index += 4

            self.log("DFGET", f"Path {i}: 0x{path_origin:04X} -> 0x{path_target:04X}")
            self.df.append({ "origin": path_origin, "target": path_target })

        self.print_all_direct_paths()
        return b'S'

    def print_node_info(self, node):
        self.log("INFO", f"Node-{node.address:04X}: ")
        self.log("INFO", f"  UUID: {node.uuid.hex()}")
        self.log("INFO", f"  Status: {node.status.name}")
        if []:
            self.log("INFO", "  Direct Paths:")
            for path in []:
                self.log("INFO", f"    → {path['origin']:04X} -> {path['target']:04X}")
    
    def print_all_nodes(self):
        self.log("INFO", "Current Nodes:")
        if not self.node_list:
            self.log("INFO", "  (none)")
            return
        for node in self.node_list:
            self.print_node_info(node)

    def print_all_direct_paths(self):
        self.log("DFGET", "Current Direct Forwarding Paths:")
        if not self.df:
            self.log("DFGET", "  (none)")
            return
        for path in self.df:
            self.log("DFGET", f"  {path['origin']:04X} -> {path['target']:04X}")
    
    def update_dashboard(self, update):
        if self.send_web:
            self.log("INFO", f"Sending dashboard update: {update}")
            self.send_web(update)
        
    def callback_uart(self, data):
        if not data or len(data) < 3:
            self.log("ERROR", f"Malformed UART data: {data}")
            return b'F'

        self.log("RAW", f"Raw UART data: {data}")
        node_addr_bytes = data[0:2]
        op_code = data[2:3]
        payload = data[3:]
        node_addr = parseNodeAddr(node_addr_bytes)
        self.log("RECEIVE", f"Processed UART from 0x{node_addr:04X}, op: {op_code.hex()}, payload: {payload}")

        if op_code == OPCODES["Net Info"]:
            self.handle_network_info(payload)
        elif op_code == OPCODES["Node Info"]:
            self.add_node("Node", node_addr, payload)
        elif op_code == OPCODES["Root Reset"]:
            self.df.clear()
        elif op_code == OPCODES["DF Info"]:
            self.handle_direct_forwarding_info(payload)
        elif op_code == OPCODES["Data"]:
            self.update_node_gps(node_addr, payload)
        else:
            self.log("INFO", f"Unhandled opcode from 0x{node_addr:04X}")
        
        self.update_dashboard({
        "nodes": [
            {
                "address": node.address,
                "status": node.status.name,
                "uuid": node.uuid.hex(),
                "gps": {
                    "lat": node.gps[0],
                    "lon": node.gps[1]
                } if node.gps else None,
                "data": {
                    k.hex(): [entry.hex() for entry in v]
                    for k, v in node.data_historys.items()
                } if node.data_historys else {}
            } 
            for node in self.node_list
        ],
        "direct_forwarding_paths": self.df
        })
                
    def callback_socket(self, data):
        command = data[0:5]
        payload = data[5:]
        self.log("RECEIVE", f"Socket command: {data}")
        
        try:
            command = command.decode('utf-8')
        except UnicodeDecodeError:
            self.log("ERROR", "Socket command decode failed")
            return b'F'
        
        if command == "NINFO":
            self.log("INFO", "NINFO command received")
            self.send_uart(b'NINFO')
            return b'S'
        elif command == "GETDF":
            self.log("INFO", "GETDF command received")
            self.send_uart(b'GETDF')
            return b'S'
        elif command == "RST-R":
            self.send_uart(b'RST-R')
            return b'S'
        elif command == "CLEAN":
            self.send_uart(b'CLEAN')
            return b'S'
        elif command == "SEND-":
            if len(payload) < 2:
                return b'F' + b"Missing target address"
            dst_addr = int.from_bytes(payload[:2], 'big')
            msg = payload[2:]
            self.send_uart(b'SEND-' + payload)
            return b'S'
        elif command == "BCAST":
            msg = payload
            self.send_uart(b'BCAST' + msg)
            return b'S'

        return b'F' + b"Unknown Command"