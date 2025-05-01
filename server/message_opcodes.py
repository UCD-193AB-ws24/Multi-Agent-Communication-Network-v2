OPCODES = {
    # Network Info (Opcode: 0x01)
    # Sent in response to the 'NINFO' command from the host.
    # Indicates a snapshot of current provisioned nodes.
    # Payload format:
    #   [0x01][batch_size][addr][uuid]...[addr][uuid]
    #       - batch_size (1 byte): Number of nodes in this batch
    #       - addr (2 bytes): Unicast address (big-endian)
    #       - uuid (16 bytes): 128-bit UUID
    # Sent in batches of up to 40 nodes.
    "Net Info": b'\x01',

    # Node Provisioned (Opcode: 0x02)
    # Sent automatically after a node completes provisioning and configuration.
    # Payload format:
    #   [0x02][uuid]
    #       - uuid (16 bytes): UUID of newly added node
    # Used to notify host without requiring full NINFO refresh.
    "Node Info": b'\x02',

    # Root Restarted (Opcode: 0x03)
    # Sent right after the root node reboots (e.g., from 'RST-R' command).
    # Payload format:
    #   [0x03]
    # No payload. Signals that runtime state has been reset (DF table, buffers).
    # Host should clear volatile state and optionally re-request NINFO and DFINFO.
    "Root Reset": b'\x03',

    # Direct Forwarding Table Info (Opcode: 0x04)
    # Sent in response to the 'DFINFO' command from the host.
    # Contains all DF paths stored by the root.
    # Payload format:
    #   [0x04][path_count][origin][target]...[origin][target]
    #       - path_count (1 byte): Number of DF paths
    #       - origin (2 bytes): Source node address (big-endian)
    #       - target (2 bytes): Destination node address (big-endian)
    # Sent in batches of up to 40 paths.
    "DF Info": b'\x04',
}

