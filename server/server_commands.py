SERVER_COMMANDS = {
    # Get Network Info
    # Command:      "NINFO"
    # Description:  Requests a snapshot of the current provisioned nodes in the mesh.
    # Root Response:
    #   - Sends one or more UART packets with opcode 0x01 (NET_INFO)
    #   - Each packet includes up to 40 nodes: [addr][uuid]
    "NINFO": b'NINFO',

    # Get Direct Forwarding Table
    # Command:      "GETDF"
    # Description:  Requests the current DF path table stored at the root.
    # Root Response:
    #   - Sends a single UART packet with opcode 0x04 (DF_INFO)
    #   - Payload: [count][origin][target]...[origin][target]
    "GETDF": b'GETDF',

    # Restart Root Node
    # Command:      "RST-R"
    # Description:  Triggers a soft reboot using esp_restart().
    # Root Response:
    #   - After reboot, sends a single byte 0x03 (ROOT_RESTARTED)
    #   - Clears RAM (DF table lost), but NVS-stored provisioned nodes remain
    "RST-R": b'RST-R',

    # Clean All Mesh State
    # Command:      "CLEAN"
    # Description:  Deletes all provisioned nodes and DF paths.
    # Root Response:
    #   - Sends a UART log string (" - Reseting Root Module\n")
    #   - No structured opcode sent (optional: host clears node/DF state)
    "CLEAN": b'CLEAN',

    # Send Unicast Message
    # Command:      "SEND-"
    # Payload:      [addr (2 bytes)] + [message bytes]
    # Description:  Sends a unicast BLE message to the specified node.
    # Root Behavior:
    #   - Sends BLE message to node at given unicast address
    #   - No acknowledgment unless the node replies
    "SEND-": b'SEND-',

    # Send Broadcast Message
    # Command:      "BCAST"
    # Payload:      [message bytes]
    # Description:  Sends a BLE broadcast message to all provisioned nodes.
    # Root Behavior:
    #   - Broadcasts to all nodes using BLE Mesh Publish
    "BCAST": b'BCAST',
}
