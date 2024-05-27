######################################################################################
# New Opcodes to be agreeed with python server (socket) and edge device (uart)
# socket:
# 'BCAST' boardcast 
# 'BCOPY' boardcast copy / confirmed recived
# 'RST-R' reset root module
# 'CNTAC' get active node count
#
# uart version:
# 'BCT' for boardcast in uart
# 'BCY' for boardcast copy in uart
# 'RST' reset root module
#
#
#
######################################################################################

# Test-Flow
# A network-measuring Python test program (not our Python server, but a lot of the same code).
# 1 -  Python test program send command to Edge-device (ras-pi) to change the test mode
# 2 - Ras-pi return confirm
# 3 - Python Bcast a pkt to start the current test and measures the metric
# 4 - Python Bcast a pkt to finish the current test
# 5 - Record Measurement

# For example: (connect 10 node speed)
# 1 - Python sends ‘Test-0’ to all edge device
# 2 - Ras-pi all confirm copy on changing test mode
# 3 - Python start timer and Broadcast ‘START’ to all ras-pi & reset ESP-root
# 4 - Ras-pi restart the ESP-edge
# 5 - Python stop timer when all 10 nodes are connected
# 6 - Python Broadcast ‘FINISH’ to stop the current test # no need for test-0 reconnect
# 7 - Record the Timestamp of each node connected 

import time
from socket_api import Socket_Manager  # class object
from socket_api import craft_message_example, getOpCodeNum, parseNodeAddr  # function
from socket_api import BLE_MESH_BOARDCAST_ADDR # constents
from master import subscribe, unsubscribe
from master import network_info as net_info

# globl variable so it can be accessed by all test and reused
network_node_amound = 0
current_test = ""
boardcast_confirmed_node = []


def field_test_boardcast_confirm_callback(data):
    node_addr = parseNodeAddr(data[0:2])
    payload = data[2:]
    try:
        payload = payload.decode()
    except:
        print(f"failed to decode payload {payload}")
        
    if payload == current_test:
        boardcast_confirmed_node.append(node_addr)

def boardcast_and_wait_for_confirm(socket_api, test_name, node_amount, timeout):
    boardcast_confirmed_node = []
    current_test = test_name
    subscribe("BCOPY", field_test_boardcast_confirm_callback)
    
    # boardcast
    message = craft_message_example("BCAST", 0, test_name) 
    socket_api.socket_sent(message)

    # timeout
    start_time = time.time
    timeout = 10

    while len(boardcast_confirmed_node) < node_amount:
        current_time = time.time
        if current_time - start_time > timeout:
            print(f"Faild to confirm {test_name} boardcast with edge device")
            print(f" - {len(boardcast_confirmed_node)} copied boardcast message")
            unsubscribe("BCOPY", field_test_boardcast_confirm_callback)
            return False
        
        time.sleep(0.1) # check every 0.1 second
    
    # recived all confirmation
    unsubscribe("BCOPY", field_test_boardcast_confirm_callback)
    return True

def send_command(socket_api, opcode, node_addr, payload):
    # send command and confirm executed successfully
    message = craft_message_example(opcode, node_addr, payload) 
    response = socket_api.socket_sent(message)
    if response[0:1] = b'F': # socket command faild
        error = response[1:]
        try:
            error = error.decode()
        except:
            pass
        print(f"Socket Command '{opcode}' failed, Error: {error}")
        return (False, error)
    
    # succeed
    response = response[1:]
    return (True, response)

def Test_0_connect_10_node(socket_api):
    # check if uart is running, root is runing, has 10 node
    # FLDTS
    global network_node_amound, boardcast_confirmed_node
    attempts = 0
    max_attempts = 3
    boardcast_timeout = 10
    conenct_node_timeout = 20
    node_amount = 10
    
    # subscribe("[NET]", test_0_network_status_callback)
    # ----------- Test 0 -----------
    while attempts < max_attempts:
        attempts += 1
        print(f"\n===== Starting test-0 with attempt-{attemps}/{max_attempts} ===== ")
        
        # boardcasr to initilize test on edge device
        success = boardcast_and_wait_for_confirm(socket_api, "TEST0", node_amount, boardcast_timeout)
        if !success:
            continue
        print(f"Initilied Test on edge by boardcast")
        
        # boardcasr to start test on edge device
        success, _ = send_command(socket_api, "BCAST", 0, "START") 
        if !success:
            continue
        print(f"Started Test on edge by boardcast")
        
        # reset root
        success, _ = send_command(socket_api, "RST-R", 0, "") 
        if !success:
            continue
        print(f"Root reseted, wating on edge connect back")
        
        # check active node count on network
        start_time = time.time
        current_time = start_time
        time_elapsed = 0
        active_count = 0
        while active_nodes < node_amount:
            current_time = time.time
            time_elapsed = current_time - start_time
            if time_elapsed > conenct_node_timeout:
                print(f"Timeout Trigered, failed to connect {node_amount} nodes in {conenct_node_timeout}")
                break
                
            success, response = send_command(socket_api, "CNTAC", 0, "")
            new_active_count = response[0]
            if active_count != new_active_count:
                print(f" - {active_count} node connected with {round(time_elapsed, 2)} second elapsed")
            
        
        if active_nodes < node_amount:
            continue
        
        
        print(f"All {node_amount} node conneceted back, test finished")
        # log result
        attempts = max_attempts + 1
        break
    
    # test finished
    if attemps == max_attempts + 1:
        print("Test0 Succeed")
        # print the result
    
    # ----------- Test 0 -----------