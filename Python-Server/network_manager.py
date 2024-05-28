import struct
import time
from node import Node, Node_Status

shared_node_list = []

class Network_Manager():
    def __init__(self):
        # Node list data struct
        # pull the node list from esp_module
        # create data structures
        global shared_node_list
        self.node_list = shared_node_list
        self.socket_sent = None
        self.uart_sent = None
        self.current_node = None
    
    def add_node(self, name: str, address: int, uuid: b''):
        node = Node(name, address, uuid)
        self.node_list.append(node)
        print(f"node {address} added")
        return node
    
    def run_on_current_thread(self):
        print("Net Manager start running")
        while True:
            # print("Net Manager still running...")
            time.sleep(1)
            
    def attack_callback(self, socket_sent, uart_sent):
        self.socket_sent = socket_sent
        self.uart_sent = uart_sent

    # getNodeData needs the pre-defined data_type & length table, (not now),  -------------------- TB Finish --------------------------
    def getNodeData(self, data_type, node_addr):
        # <= data outgoing (single or patch)
        # S|data_type|data_length_byte|size_n|node_addr/index_0|data_0|...|node_addr/index_n|data_n
        # ^ success
        # F|Error_flag/Message
        response = b'S' + data_type.encode()
        
        if data_type != "GPS":
            print("only support GPS for testing, need define length of other data type in doc")
            return b'F-only support for GPS'

        # ============== need to be remake for correct data length ===================
        # TB Finish
        # ----- predefined data length for each type -------
        data_length_byte = 6 # 6 byte for GPS data
        response += data_length_byte.to_bytes(1, byteorder='little') # one byte for size, we won't have some data larger than 255 bytes
        # ----- predefined data length for each type -------
        
        
        # ------ untested get all node feature ---------------
        if node_addr == 255: # 0xFF => all nodes in same patch
            active_nodes = list(filter(lambda node: node.status == Node_Status.Active, self.node_list))
            size_n = len(active_nodes)
            response += size_n.to_bytes(1, byteorder='little') # one byte for size, we won't have more than 254 nodes
            for node in active_nodes:
                response += node.address.to_bytes(1, byteorder='little')
                response += node.getDataBytes(data_type)
        # ------ untested get all node feature ---------------

        elif node_addr != 255: # 0x## => single node
            node_list = list(filter(lambda node: node.address == node_addr, self.node_list))
            if len(node_list) == 0:
                error = "Node Not Found"
                response = b'F' + len(error).to_bytes(1, byteorder='little') + error.encode()
                return response
            
            response += b'\x01' # only one node
            node = node_list[0]
            response += node.address.to_bytes(1, byteorder='little')
            response += node.getDataBytes(data_type)

        # ============== need to be remake for correct data length ===================
        
        return response
        
    # updateNodeData needs the pre-defined data_type & length table, (not now),  -------------------- TB Finish --------------------------
    def updateNodeData(self, node_addr: int, msg_payload: bytes):
        # print("updateNodeData from cmd:[D] on node:", node_addr) # [Testing Log]
        node_list = list(filter(lambda node: node.address == node_addr, self.node_list))
        if len(node_list) <= 0:
            node = self.add_node("Node",node_addr, b'')
        else:
            node = node_list[0]
        
        #   size_n|data_type|data_length_byte|data|...|data_type|data_length_byte|data
        #    1   |   3     |     1          | n| ... (size of each segment in bytes)
        size = msg_payload[0]
        
        data_start = 1
        for n in range(size):
            data_type = msg_payload[data_start : data_start+3]
            data_len = msg_payload[data_start+3]
            
            # print(f"data_type:{data_type}, data_len:{data_len}") # [Testing Log]
            
            try:
                data_type = data_type.decode('utf-8') # use string name if is a string name
            except:
                pass
            
            data = msg_payload[data_start+4: data_start+4+data_len]
        
            node.storeData(data_type, data)
            # print(f"[Node] addr-{node_addr} added {data_type} data") # [Testing Log] 
            data_start += 4 +  data_len
        
        print("done updating node:", node_addr)
            
# ============================= Socket Callback Logics =================================
    def callback_socket(self, data):
        print(f"\n[Socket-CB] {data}") # [Testing Log]
        command = data[0:5]
        payload = data[5:]
        try:
            command = command.decode('utf-8')
        except:
            print("[Socket] can't parse command", command)
            return b'F'
        
         ############## Command get handled in Server ##############
        if command == "[GET]": # Get data
            # [GET]|data_type|node_addr/index
            # node_addr = socket.ntohs(payload[0:2]) # int.from_bytes(payload[3], byteorder='little')
            node_addr = parseNodeAddr(payload[0:2]) # unpack 2 byte and converts them from network byte order to host byte order
            data_type = payload[2:5].decode('utf-8')
            return self.getNodeData(data_type, node_addr)
        
        if command == "ACT-C": # Count active node
            target_status = Node_Status.Active
            node = list(filter(lambda node: node.status == target_status, self.node_list))
            count = len(node) % 255 # will not exceed, just in case get "OverflowError" from encode
            return b'S' + count.to_bytes(1, byteorder='big')
        
        if command == "NSTAT": # retrive network node status
            pass    
        
        if command == "NINFO": # retrive network node info
            # ask net_info from esp-root, give it to socket API
            pass
        
         ############## Command get handled in ESP-Root-Module ##############
        # all other commands
        # - 'SEND-' send message
        # - 'BCAST' broadcast message
        # - 'RST-R' reset root module
        # send to ESP-Root-Module by uart
        return self.uart_sent(data)

# ============================= UART Callback Logics =================================
    def callback_uart(self, data):
        print(f"\n[UART-CB]:  {data}") # [Testing Log]
        node_addr_bytes = data[0:2]
        op_code = data[2:5]
        payload = data[5:]
        
        node_addr = parseNodeAddr(node_addr_bytes) # unpack 2 byte and converts them from network byte order to host byte order
        try:
            op_code = op_code.decode('utf-8')
        except:
            print("[Uart] can't parse opcode", op_code)
            return b'F'
        
        ############## Opcodes only updates python server ############## 
        if op_code == "[D]": # Data update
            self.updateNodeData(node_addr, payload)
            return b'S'
            
        if op_code == "NET": # Network Information
            return b'S'
            
        if op_code == "RST": # Root Module restart and back online
            return b'S'
            
        if op_code == "NOD": # Node Connected (become avaiable) Update
            node_uuid = payload
            node_list = list(filter(lambda node: node.address == node_addr, self.node_list))
            if len(node_list) <= 0:
                node = self.add_node("Node",node_addr, node_uuid)
            else:
                node = node_list[0]
                node.uuid = node_uuid
                node.status = Node_Status.Active
            return b'S'
            
        ############## other Opcodes pass to client-API using socket ##############
        return self.socket_sent(data)

# ======================= End of Network Manager Class ================================

# Other Utility Function
def encodeNodeAddr(addr: int) -> bytes:
    return struct.pack('!H', node_addr) # encoded from host to network endianess (byte order)

def parseNodeAddr(addr_bytes: bytes) -> int:
    # parse 2 byte into number
    return struct.unpack('!H', addr_bytes)[0] # decode 2 byte from network to host endianess (byte order)