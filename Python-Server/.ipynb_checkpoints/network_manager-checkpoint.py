import struct
import time
import json
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
        self.web_socket_send_to_web = None
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
            
    def attach_callback(self, socket_sent, uart_sent,  web_socket_send_to_web):
        self.socket_sent = socket_sent
        self.uart_sent = uart_sent
        self.web_socket_send_to_web = web_socket_send_to_web

    def getActiveNode(self):
        # TB Finish, update on node status base on timestamp
        active_nodes = list(filter(lambda node: node.status == Node_Status.Active, self.node_list))
        return active_nodes
        
    def getNodeData(self, data_type, node_addr):
        # <= data outgoing (single or patch)
        # S|data_type|data_length_byte|size_n|node_addr/index_0|data_0|...|node_addr/index_n|data_n
        # ^ success
        # F|Error_flag/Message
        response = b'S' + data_type.encode()

        # ============== need to be remake for correct data length ===================
        # TB Tested - need full test and review
        
        # ------ untested get all node feature ---------------
        if node_addr == 0: # 0x0000 => get all nodes in same patch
            active_nodes = self.getActiveNode()
            data_len = 0
            # load length
            for node in active_nodes:
                hasData, data_len = node.getDataLength(data_type)
                if hasData:
                    response += data_len.to_bytes(1, byteorder='little')
                    break

            # load data
            size_n = 0
            total_data_bytes = b''
            for node in active_nodes:
                hasData, data = node.getDataBytes(data_type)
                if hasData:
                    size_n += 1
                    total_data_bytes += encodeNodeAddr(node.address)
                    total_data_bytes += data
                    
            response += size_n.to_bytes(1, byteorder='little') # one byte for size, we won't have more than 254 nodes
            response += total_data_bytes
            return response
        # ------ untested get all node feature ---------------

        elif node_addr != 0: # 0x## => single node
            node_list = list(filter(lambda node: node.address == node_addr, self.node_list))
            if len(node_list) == 0:
                error = "Node Not Found"
                response = b'F' + len(error).to_bytes(1, byteorder='little') + error.encode()
                return response
            
            response += b'\x01' # size_n = 1 only one node
            node = node_list[0]
            hasData, data = node.getDataBytes(data_type)
            if not hasData:
                error = "Data Type Not Found"
                response = b'F' + len(error).to_bytes(1, byteorder='little') + error.encode()
                return response
                
            response += encodeNodeAddr(node.address)
            response += data
            return response

        # ============== need to be remake for correct data length ===================
    
    def updateNodeData(self, node_addr: int, msg_payload: bytes):
        # print("updateNodeData from cmd:[D] on node:", node_addr) # [Testing Log]
        node_list = list(filter(lambda node: node.address == node_addr, self.node_list))
        if len(node_list) <= 0:
            node = self.add_node("Node",node_addr, b'')
        else:
            node = node_list[0]

        node.status = Node_Status.Active
        
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
            network_status = {
                "node_amount" : 0,
                "node_addr_list": [],
                "node_status_list": []
            }
            network_status["node_amount"] = len(self.node_list)
            network_status["node_addr_list"] = list(map(lambda node: node.address, self.node_list))
            network_status["node_status_list"] = list(map(lambda node: 1 if node.status == Node_Status.Active else 0, self.node_list))
            
            # Serialize and Send JSON data
            network_status_json = json.dumps(network_status)
            network_status_bytes = network_status_json.encode('utf-8')
            print(f"'NSTAT' command executed")
            return b'S' + network_status_bytes
        
        if command == "NINFO": # retrive network node info
            # ask net_info from esp-root, give it to socket API
            return b'F' + "Not implmented".encode('utf-8')
            
         ############## Command pass to web monitor ##############
        if command == "W-LOG": # log traffic to website
            # payload is log message
            self.web_log(payload)
            
        if command == "W-RBT": # update robot status to website
            # payload is robot status list
            self.web_robot_status_update(payload)

            
        
         ############## Command get handled in ESP-Root-Module ##############
        # all other commands
        # - 'SEND-' send message
        # - 'BCAST' broadcast message
        # - 'RST-R' reset root module
        # send to ESP-Root-Module by uart
        if command == "RST-R":
            # self.node_list = [] # reset server node list as well
            # set nodes to not avaiable for now , TB Finished
            for node in self.node_list:
                node.status = Node_Status.Disconnect
            
            self.uart_sent(data) # since root module will reset, it will not return anything
            self.web_node_status_update()
            self.web_log(f"==== Reseting the network ====")
            return b'S'

        # pass command to uart
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
            self.web_log(f"[D] recived update from Node-{node_addr}")
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
            print(f"Node-{node_addr} connected")
            self.web_log(f"Node-{node_addr} connected")
            self.web_node_status_update()
            return b'S'
            
        ############## other Opcodes pass to client-API using socket ##############
        return self.socket_sent(data)


# ============================= Web socket send Logics =================================
    def web_log(self, message):
        data = {
            "type": "trafficLog",
            "message": message
        }
        self.web_socket_send_to_web(data)
        
    def web_connection_update(self, socket_connection, uart_connection):
        data = {
            "type": "networkStatus",
            "status": "connectionStatus",
            "socket": socket_connection,
            "uart": uart_connection
        }
        self.web_socket_send_to_web(data)

    def web_node_status_update(self):
        self.node_list
        data = {
            "type": "networkStatus",
            "status": "nodeStatus",
            "nodes": []
        }

        for node in self.node_list:
            node_info = {"name": "", "status": ""}
            node_info["name"] = "Node-" + node.address

            node_info["status"] = "normal"
            if node.status != Node_Status.Active:
                node_info["status"] = "error"
                
            data["nodes"].append(node_info)
        
        self.web_socket_send_to_web(data)
        
    def web_robot_status_update(self, robot_data_list):
        # Example
        # "robots": [
        #     { "id": 1, "name": "Robot Node 1", "state": "Active", "node": 'Node-0' },
        #     { "id": 2, "name": "Robot Node 2", "state": "Active", "node": 'Node-1' }
        # ]
        self.node_list
        data = data = {
            "type": "networkStatus",
            "status": "robotStatus",
            "robots": robot_data_list
        }
        
        self.web_socket_send_to_web(data)

                
# ======================= End of Network Manager Class ================================

# Other Utility Function
def encodeNodeAddr(node_addr: int) -> bytes:
    return struct.pack('!H', node_addr) # encoded from host to network endianess (byte order)

def parseNodeAddr(addr_bytes: bytes) -> int:
    # parse 2 byte into number
    return struct.unpack('!H', addr_bytes)[0] # decode 2 byte from network to host endianess (byte order)