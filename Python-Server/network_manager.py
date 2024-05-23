import struct
import time
from node import Node

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
    
    def add_node(self, name, address, uuid):
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

    # ============================= Socket Logics =================================
    # getNodeData needs the pre-defined data_type & length table, (not now),  -------------------- TB Finish --------------------------
    def getNodeData(self, data_type, node_addr):
        # <= data outgoing (single or patch)
        # S|data_type|data_length_byte|size_n|node_addr/index_0|data_0|...|node_addr/index_n|data_n
        # ^ success
        # F|Error_flag/Message
        data = b'S' + data_type.encode()
        
        if data_type != "GPS":
            print("only support GPS for testing, need define length of other data type in doc")
            return b'F-only support for GPS'

        # ============== need to be remake for correct data length ===================
        # TB Finish
        # ----- predefined data length for each type -------
        data_length_byte = 6 # 6 byte for GPS data
        data += data_length_byte.to_bytes(1, byteorder='little') # one byte for size, we won't have some data larger than 255 bytes
        # ----- predefined data length for each type -------
        
        
        # ------ untested get all node feature ---------------
        if node_addr == 255: # 0xFF => all nodes in same patch
            active_nodes = list(filter(lambda node: node.status == Node_Status.Active, self.node_list))
            size_n = len(active_nodes)
            data += size_n.to_bytes(1, byteorder='little') # one byte for size, we won't have more than 254 nodes
            for node in active_nodes:
                data += node.address.to_bytes(1, byteorder='little')
                data += node.getDataBytes(data_type)
        # ------ untested get all node feature ---------------

        elif node_addr != 255: # 0x## => single node
            node = list(filter(lambda node: node.address == node_addr, self.node_list))
            if len(node) == 0:
                error = "Node Not Found"
                data = b'F' + len(error).to_bytes(1, byteorder='little') + error.encode()
                return data
            
            data += b'\x01' # only one node
            node = node[0]
            data += node.address.to_bytes(1, byteorder='little')
            data += node.getDataBytes(data_type)

        # ============== need to be remake for correct data length ===================
        
        return data
        
    def callback_socket(self, data):
        print(f"\n[Socket-CB] {data}") # [Testing Log]
        op_code = data[0:5]
        payload = data[5:]
        try:
            op_code = op_code.decode('utf-8')
        except:
            print("[Socket] can't parse opcode", op_code)
            return b'F'
            
        if op_code == "[GET]":
            # [GET]|data_type|node_addr/index
            # node_addr = socket.ntohs(payload[0:2]) # int.from_bytes(payload[3], byteorder='little')
            node_addr = struct.unpack('!H', payload[0:2])[0] # unpack 2 byte and converts them from network byte order to host byte order
            data_type = payload[2:5].decode('utf-8')
            return self.getNodeData(data_type, node_addr)
            
        #----------TB_review : response--------------
        if op_code == "[REQ]":
            # restructure response to Edge Request base on uart format, send back to edge node
            node_addr = data[5:7]
            uart_opcode = "<R>".encode()
            payload = data[7:]
            
            uart_msg = node_addr + uart_opcode + payload
            self.uart_sent(uart_msg)
            return b'S'
        # -------------------------------------------
        
        # # faking uart request -----------------------
        # op_code = data[0:3].decode('utf-8')
        # if op_code == "<Q>":
        #     addr = data[3:5]
        #     payload = data[5:]
        #     lenth = 14
        #     new_data = addr + "<Q>".encode() +lenth.to_bytes(1, "little")  + payload
        #     print(new_data)
        #     self.callback_uart(new_data)
        #     return b'S'
        # #


    # ============================= UART Logics =================================
    # updateNodeData needs the pre-defined data_type & length table, (not now),  -------------------- TB Finish --------------------------
    def updateNodeData(self, node_addr, msg_payload):
        # print("updateNodeData from cmd:[D] on node:", node_addr) # [Testing Log]
        node = list(filter(lambda node: node.address == node_addr, self.node_list))
        if len(node) <= 0:
            node = self.add_node("Node",node_addr, None)
        else:
            node = node[0]
        
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
        
    def callback_uart(self, data):
        print(f"\n[UART-CB]:  {data}") # [Testing Log]
        node_addr = data[0:2]
        op_code = data[2:5]
        payload = data[5:]
        
        
        node_addr = struct.unpack('!H', node_addr)[0] # unpack 2 byte and converts them from network byte order to host byte order
        try:
            op_code = op_code.decode('utf-8')
        except:
            print("[Uart] can't parse opcode", op_code)
            return b'F'
        
        # Process Message
        if op_code == "[D]":
            # Data update
            self.updateNodeData(node_addr, payload)
            
        
        #--------TB_review : response----------------
        if op_code == "<Q>":
            # restructure message base on socket message format, transfer the request to C-Client-API
            socket_op_code = "[REQ]".encode()
            request_msg = socket_op_code + node_addr.to_bytes(2, byteorder='little') + payload
            self.socket_sent(request_msg)
        # -------------------------------------------

        # make a case let custom (unindentified cases) pass to socket
    
        # print("> uart callback done")  # [Testing Log]