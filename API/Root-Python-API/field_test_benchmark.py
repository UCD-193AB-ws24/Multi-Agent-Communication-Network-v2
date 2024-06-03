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
from opcode_subscribe import subscribe, unsubscribe

# globl variable so it can be accessed by all test and reused
network_node_amound = 0
current_test = ""
broadcast_confirmed_node = []
# this is for holding result from any callback function
# one should be enough since the test code is serial there is only one current_test, so only one callback function should be active
# if late response come in from old test, it the call back function should set to be ignored
result_from_callback = {}


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
    start_time = time.time()
    timeout = 10

    while len(broadcast_confirmed_node) < node_amount:
        current_time = time.time()
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

def connect_N_node(socket_api, node_amount):
    # check if uart is running, root is runing, has 10 node
    # FLDTS
    global network_node_amound, broadcast_confirmed_node
    attempts = 0
    max_attempts = 3
    broadcast_timeout = 10
    conenct_node_timeout = 20
    # node_amount = 10
    
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
        start_time = time.time()
        current_time = start_time
        time_elapsed = 0
        active_count = 0
        while len(broadcast_confirmed_node) < node_amount:
            current_time = time.time()
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
        current_time = time.time()
        time_elapsed = current_time - start_time
        print("Connect N node Succeed, time: ", round(time_elapsed, 2) , "s")
        # print the result
    else:
        print("Connect N node Failed")
    # ----------- Test 0 -----------
    
    
def ping_N_node_callback(message: bytes):
    # need to make sure the current test is still correct, if it's message from a old test, ignore it
    # if current_test != "Ping_N_Node":
    #     return
    end_time = time.time()
    node_addr = parseNodeAddr(message[0:2])
    opcode = message[2:5] # subscriped opcode 'CPY'
    payload = message[5:]
    
    try:
        payload = payload.decode()
    except:
        print(f"failed to decode payload {payload}")
        return
    if opcode != "CPY":
        print(f"wrong copy message, not 'CPY' - test initialization")
        return
    if payload[0] != "P":
        print(f"wrong copy message, not 'P' - ping response")
        return
        
    old_tuple = result_from_callback[node_addr]
    start_time = old_tuple[3]
    total_time = old_tuple[2]
    result_from_callback[node_addr] = (old_tuple[0] ,old_tuple[1] + 1, total_time + (end_time - start_time), 0.0)

def ping_N_node(socket_api, node_amount, data_size, send_rate, time) -> tuple[bool, str]:
    # measure RTT and Pkt loss for sending
    # ping <node_amount> node, <data_size> bytes paket on <send_rate> over <time> second
    # assume the send_rate is how many time between each send
    # if is by HZ then uncomment the following code
    
    # send_rate = 1/send_rate  # 1/Hz = second
    
    # asssume we populate the broadcast_confirmed_node[] first through test_initialize() before calling this function
    #  based on the test_initialize() functin's name it will becalled before this function.
    
    ping_packet_timeout_time = 1
    send_rate = send_rate / node_amount # because there are multiple nodes to be pinged, so total sleep time is less
    subscribe("CPY", ping_N_node_callback)
    if node_amount > len(broadcast_confirmed_node):
        return [False, "Not enough node connected in the network"]
    if data_size < 6: #  2 address + 3 opcode + payload size minimum of 1 'p'
        return [False, "Data size too small"]
    payload = "CPY" + 'P' * (data_size-5) # minus 2 addr and 3 opcode = -5
    
    #initialize dictionary
    for i in range(node_amount):
        ping_dict = {}
        ping_dict[broadcast_confirmed_node[i]] = (0,0, 0.0, 0.0) # (number_of_packet_send, numbe_of_packet_received, total_time, start_time)  
        result_from_callback = ping_dict
    
    ping_start_time = time.time()
    # while withiin the pinging time
    while time.time() - ping_start_time < time:
        for i in range(node_amount):
            start_time = time.time()
            old_tuple = result_from_callback[broadcast_confirmed_node[i]]
            result_from_callback[broadcast_confirmed_node[i]] = (old_tuple[0]+1, old_tuple[1], old_tuple[2], start_time)
            send_command(socket_api, "SEND-", broadcast_confirmed_node[i], payload)
            time.sleep(send_rate)
    
    # leave the timeout_time for the last packet to return
    print("End of sending Ping request, Waiting for last response packet")
    time.sleep(ping_packet_timeout_time)
    
    # calculate and print the result of ping
    for i in range(node_amount):
        result = result_from_callback[broadcast_confirmed_node[i]]
        print(f"Edge Node {broadcast_confirmed_node[i]}: packet loss: {result[0]-result[1]}/{result[0]}; AVG_RTT: {result[2]/result[1]}")
    
    # reset dictionary and callback function that subscribed to "CPY" opcode
    unsubscribe("CPY", ping_N_node_callback)
    result_from_callback = {}
    

    
def request_test(node_amount, request_name):
    # measure RTT and Pkt loss for sending
    # ping <node_amount> node, <data_size> bytes paket on <send_rate> over <time> second
    pass


def test_initialization(socket_api,test_name,  node_amount, broadcast_timeout):
    # broadcast 'TST|I|test_name' (test init) to initilize test on edge device
    success = broadcast_initialization_and_wait_for_confirm(socket_api, test_name, node_amount, broadcast_timeout)
    if not success:
        return False

def test_start(socket_api, node_amount, node_addr):
    # broadcast 'TST|S' (test start) to edge device
    command = "BCAST"
    if node_amount == 1:
        command = "SEND-"

    success, _ = send_command(socket_api, command, node_addr, "TSTS") 
    if not success:
        return False
    print(f"Started Test on edge")
    return True

def test_termination(socket_api):
    # broadcast 'TST|F' (test finish) to edge device
    success, _ = send_command(socket_api, "BCAST", 0, "TSTF") 
    if not success:
        return False
    print(f"Finished Test on edge by broadcast")
    return True