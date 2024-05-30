######################################################################################
# ble_network_command | dst_node_addr |          message        |
#       5 byte        |     2 byte    | 3 byte opcode | payload |
#
# === Network Command  === (5 byte)
# 'NINFO' get network info
# 'SEND-' send message
# 'BCAST' broadcast message
# 'RST-R' reset root module
# 'ACT-C' get active node count
#
# '[GET]' get node data
# 
#
# === API opcode / message type (opcode) === (3 byte)
# 'ECH' for echo message, expecting copy
# 'CPY' for copy message on recived 'ECH'
# 'REQ' edge request
#
# 'NET' Network Information message
# 'NOD' Node Connecetd update message
# 'RST' root module reseted
# '[D]' node data
#
# 'TST' for field test test-flow
# 'TST|I|test_name' expecting copy on edge confirmed test initialization
# 'TST|S' start test
# 'TST|F' finish test
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
from socket_api import craft_message_example, parseNodeAddr  # function
from master import subscribe, unsubscribe
from master import network_info as net_info

# globl variable so it can be accessed by all test and reused
network_node_amound = 0
current_test = ""
broadcast_confirmed_node = []


def field_test_broadcast_confirm_callback(message: bytes):
    node_addr = parseNodeAddr(message[0:2])
    opcode = message[2:5] # subscriped opcode 'CPY'
    payload = message[5:]
    
    try:
        payload = payload.decode()
    except:
        print(f"failed to decode payload {payload}")
        return
    
    if payload[0] != "I":
        print(f"wrong copy message, not 'I' - test initialization")
        return
        
    test_name = payload[1:]
    if test_name == current_test:
        broadcast_confirmed_node.append(node_addr)

def broadcast_initialization_and_wait_for_confirm(socket_api, test_name, node_amount, timeout):
    broadcast_confirmed_node = []
    current_test = test_name
    
    # subscribe on copy message that will get sendback from edge 
    # after broadcasting 'ECH' message
    subscribe("CPY", field_test_broadcast_confirm_callback)
    
    # broadcast 'ECH' (echo) message - expecting copy from edge
    #            test  initialize  test_name
    message_str = "TST" + "I" + test_name
    message_byte = craft_message_example("BCAST", 0, message_str.encode()) 
    socket_api.socket_sent(message_byte)

    # timeout
    start_time = time.time
    timeout = 10

    while len(broadcast_confirmed_node) < node_amount:
        current_time = time.time
        if current_time - start_time > timeout:
            print(f"Faild to confirm {test_name} broadcast with edge device")
            print(f" - {len(broadcast_confirmed_node)} copied broadcast message")
            unsubscribe("CPY", field_test_broadcast_confirm_callback)
            return False
        
        time.sleep(0.1) # check every 0.1 second
    
    # recived all confirmation
    unsubscribe("CPY", field_test_broadcast_confirm_callback)
    return True

def send_command(socket_api, command: str, node_addr: int, payload: bytes) -> tuple[bool, bytes]:
    # send command and confirm executed successfully
    message = craft_message_example(command, node_addr, payload) 
    response = socket_api.socket_sent(message)
    if response[0:1] == b'F': # socket command faild
        error = response[1:]
        try:
            error = error.decode()
        except:
            pass
        print(f"Socket Command '{command}' failed, Error: {error}")
        return (False, error)
    
    # succeed
    response = response[1:]
    return (True, response)

def Test_0_connect_10_node(socket_api):
    # check if uart is running, root is runing, has 10 node
    # FLDTS
    global network_node_amound, broadcast_confirmed_node
    attempts = 0
    max_attempts = 3
    broadcast_timeout = 10
    conenct_node_timeout = 20
    # node_amount = 10
    node_amount = 1
    
    # subscribe("[NET]", test_0_network_status_callback)
    # ----------- Test 0 -----------
    while attempts < max_attempts:
        attempts += 1
        print(f"\n===== Starting test-0 with attempt-{attempts}/{max_attempts} ===== ")
        
        # broadcast 'TST|I|name' (test init) to initilize test on edge device
        success = broadcast_initialization_and_wait_for_confirm(socket_api, "TEST0", node_amount, broadcast_timeout)
        if not success:
            continue
        print(f"Initilied Test on edge by broadcast")
        
        # broadcast 'TST|S' (test start) to edge device
        success, _ = send_command(socket_api, "BCAST", 0, "TSTS") 
        if not success:
            continue
        print(f"Started Test on edge by broadcast")
        
        # reset root
        success, _ = send_command(socket_api, "RST-R", 0, "") 
        if not success:
            continue
        print(f"Root reseted, wating on edge connect back")
        
        # check active node count on network
        start_time = time.time
        current_time = start_time
        time_elapsed = 0
        active_count = 0
        while len(broadcast_confirmed_node) < node_amount:
            current_time = time.time
            time_elapsed = current_time - start_time
            if time_elapsed > conenct_node_timeout:
                print(f"Timeout Trigered, failed to connect {node_amount} nodes in {conenct_node_timeout}")
                break
                
            success, response = send_command(socket_api, "ACT-C", 0, "")
            new_active_count = response[0]
            if active_count != new_active_count:
                print(f" - {active_count} node connected with {round(time_elapsed, 2)} second elapsed")
            
            time.sleep(0.1) # checking every 0.1 second
            
        # check if is a timeout that break the loop
        if len(broadcast_confirmed_node) < node_amount:
            continue
        
        # test succeed, all node connecetd
        print(f"All {node_amount} node conneceted back, test finished")
        # log result
        attempts = max_attempts + 1
        break
    
    # test finished
    if attempts == max_attempts + 1:
        current_time = time.time
        time_elapsed = current_time - start_time
        print("Test0 Succeed, time: ", round(time_elapsed, 2) , "s")
        # print the result
    else:
        print("Test0 Failed")
    # ----------- Test 0 -----------