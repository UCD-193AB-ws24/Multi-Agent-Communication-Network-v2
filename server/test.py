import asyncio
from network_manager import NetworkManager
from socket_manager import SocketManager
from uart_manager import UartManager
from websocket_server import WebsocketServer

PACKET_SIZE = 1024
SERVER_SOCKET_PORT = 5001
WEBSOCKET_PORT = 7654
SERIAL_PORT = "/dev/tty.usbserial-1440"
BAUD_RATE = 115200

async def main():
    uart_manager = UartManager(SERIAL_PORT, BAUD_RATE)
    socket_manager = SocketManager(SERVER_SOCKET_PORT, PACKET_SIZE)
    websocket_server = WebsocketServer(host="localhost", port=WEBSOCKET_PORT)
    network_manager = NetworkManager()

    socket_manager.attach_callback(network_manager.callback_socket)
    uart_manager.attach_callback(network_manager.callback_uart)
    network_manager.attach_callback(
        socket_manager.send_data, uart_manager.send_data, websocket_server.send_data
    )

    uart_manager.run()
    socket_manager.run()
    websocket_server.run()
    
    await asyncio.sleep(3)
    
    while True:
        socket_command = b"NINFO"
        network_manager.callback_socket(socket_command)
        await asyncio.sleep(10)
        
        socket_command = b"GETDF"
        network_manager.callback_socket(socket_command)
        await asyncio.sleep(20)
        
        # PRINTING NETWORK INFO
        print("\n[TEST] Printing network info...")
        network_manager.print_all_nodes()
        network_manager.print_all_direct_paths()
        
    
    # socket_command = b"NINFO"
    # network_manager.callback_socket(socket_command)
    
    # while True:
    #     await asyncio.sleep(5)

    # NET INFO (0x01)
    # print("\n[TEST] Simulating NET INFO (0x01) batch 1/3...")
    # uart_data = (
    #     b'\x00\x00\x01\x03' +             # Dummy bytes + opcode 0x01 + 3 nodes
    #     b'\x00\x01' + b'\x01' * 16 +      # Node 0x0001, UUID = 0x01 * 16
    #     b'\x00\x02' + b'\x02' * 16 +      # Node 0x0002, UUID = 0x02 * 16
    #     b'\x00\x03' + b'\x03' * 16        # Node 0x0003, UUID = 0x03 * 16
    # )
    # network_manager.callback_uart(uart_data)
    
    # await asyncio.sleep(3)

    # print("\n[TEST] Simulating NET INFO (0x01) batch 2/3...")
    # uart_data = (
    #     b'\x00\x00\x01\x02' +             # Dummy bytes + opcode 0x01 + 2 nodes
    #     b'\x00\x04' + b'\x04' * 16 +      # Node 0x0004, UUID = 0x04 * 16
    #     b'\x00\x05' + b'\x05' * 16        # Node 0x0005, UUID = 0x05 * 16
    # )
    # network_manager.callback_uart(uart_data)
    
    # await asyncio.sleep(3)

    # print("\n[TEST] Simulating NET INFO (0x01) batch 3/3...")
    # uart_data = (
    #     b'\x00\x00\x01\x04' +         # Dummy bytes + opcode 0x01 + 4 nodes
    #     b'\x00\x01' + b'\x01' * 16 +  # Node 0x0001 with UUID 0x01 * 16
    #     b'\x00\x02' + b'\x02' * 16 +  # Node 0x0002 with UUID 0x02 * 16
    #     b'\x00\x04' + b'\x04' * 16 +  # Node 0x0004, UUID = 0x04 * 16
    #     b'\x00\x05' + b'\x05' * 16    # Node 0x0005, UUID = 0x05 * 16
    # )
    # network_manager.callback_uart(uart_data)
    
    # await asyncio.sleep(3)

    # # NODE INFO (0x02)
    # print("\n[TEST] Simulating NODE INFO (0x02) for Node-0x000E...")
    # uart_data = b'\x00\x0e\x02\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab\xab'
    # network_manager.callback_uart(uart_data)
    
    # await asyncio.sleep(3)
    
    # # PRINTING NETWORK INFO
    # print("\n[TEST] Printing network info...")
    # network_manager.print_all_nodes()
    # network_manager.print_all_direct_paths()
    
    # await asyncio.sleep(3)

    # # DF INFO (0x04)
    # dfinfo_payload = (
    #     b'\x04'  # opcode
    #     + b'\x05'  # number of paths
    #     + b'\x00\x0C\x00\x0A'
    #     + b'\x00\x0A\x00\x05'
    #     + b'\x00\x05\x00\x04'
    #     + b'\x00\x04\x00\x0E'
    #     + b'\x00\x05\x00\x00'
    # )
    # dfinfo_uart_data = b'\x00\x00' + dfinfo_payload
    # print("\n[TEST] Simulating DFINFO (0x04)...")
    # network_manager.callback_uart(dfinfo_uart_data)
    
    # await asyncio.sleep(3)
    
    # # ROOT RESET (0x03)
    # root_reset_payload = (
    #     b'\x03'
    #     + b'Reset triggered'
    # )
    # root_reset_uart_data = b'\x00\x00' + root_reset_payload
    # print("\n[TEST] Simulating Root Reset (0x03)...")
    # network_manager.callback_uart(root_reset_uart_data)
    
    # await asyncio.sleep(3)
    
    # # PRINTING NETWORK INFO
    # print("\n[TEST] Printing network info...")
    # network_manager.print_all_nodes()
    # network_manager.print_all_direct_paths()
    
    # await asyncio.sleep(3)
    
    # # DF INFO (0x04)
    # dfinfo_payload = (
    #     b'\x04'  # opcode
    #     + b'\x05'  # number of paths
    #     + b'\x00\x0B\x00\x03'
    #     + b'\x00\x03\x00\x02'
    #     + b'\x00\x02\x00\x04'
    #     + b'\x00\x04\x00\x0E'
    #     + b'\x00\x0E\x00\x01'
    # )
    # dfinfo_uart_data = b'\x00\x00' + dfinfo_payload
    # print("\n[TEST] Simulating DFINFO (0x04)...")
    # network_manager.callback_uart(dfinfo_uart_data)
    
    # await asyncio.sleep(3)
    
    # # UNHANDLED OPCODE (0x05)
    # unhandled_opcode_payload = (
    #     b'\x05'  # opcode
    #     + b'\x01'  # number of paths
    #     + b'\x00\x0C\x00\x0A'
    # )
    # unhandled_opcode_uart_data = b'\x00\x00' + unhandled_opcode_payload
    # print("\n[TEST] Simulating unhandled opcode (0x05)...")
    # network_manager.callback_uart(unhandled_opcode_uart_data)
    
    # await asyncio.sleep(3)
    
    # PRINTING NETWORK INFO
    # print("\n[TEST] Printing network info...")
    # network_manager.print_all_nodes()
    # network_manager.print_all_direct_paths()
    
    # await asyncio.sleep(3)
    
    # SEND- and BCAST commands
    # print("\n[TEST] Simulating program sending SEND- command to node 0x0005 with message 'hello'")
    # socket_command = b"SEND-" + b"\x00\x05" + b"hello"
    # network_manager.callback_socket(socket_command)

    # print("\n[TEST] Simulating program sending BCAST command to all nodes with message 'stop'")
    # socket_command = b"BCAST" + b"\x00\x00" + b"world"
    # network_manager.callback_socket(socket_command)
    
    # NINFO command
    # print("\n[TEST] Simulating program sending NINFO command to server")
    # socket_command = b"NINFO"
    # network_manager.callback_socket(socket_command)
    
    # await asyncio.sleep(3)
    
    # # PRINTING NETWORK INFO
    # print("\n[TEST] Printing network info...")
    # network_manager.print_all_nodes()
    # network_manager.print_all_direct_paths()
    
    # await asyncio.sleep(3)
    
    # # PRINTING DF INFO
    # print("\n[TEST] Simulating program sending GETDF command to server")
    # socket_command = b"GETDF"
    # network_manager.callback_socket(socket_command)
    
    # await asyncio.sleep(10)
    
    # # PRINTING NETWORK INFO
    # print("\n[TEST] Printing network info...")
    # network_manager.print_all_nodes()
    # network_manager.print_all_direct_paths()
    
    # await asyncio.sleep(3)
    
    # print("\n[TEST] Simulating Data Opcode (0x44, 'D') GPS update...")
    # uart_data = b'\x12\x34' + b'D' + b'\x01' + b'\x01' + b't$\xfe\x90\x96\x00'
    # network_manager.callback_uart(uart_data)
    
    # await asyncio.sleep(3)
    
    # Simulating GPS Data (0x05)
    # uart_data = (
    #     b'\x00\x01' + b'\x05' + b'\x01' + b'\x05' +
    #     b'\x8F\xC2\xF5\x28\x5C\x8B\x43\x40' +     # lat = 38.541 (little endian)
    #     b'\x9A\x99\x99\x99\x99\x99\x5E\xC0'       # lon = -121.775 (little endian)
    # )

    # print("\n[TEST] Simulating GPS Data (Opcode 0x05) from 0x0001")
    # network_manager.callback_uart(uart_data)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[MAIN] KeyboardInterrupt caught outside event loop.")