import asyncio
from network_manager import NetworkManager
from uart_manager import UartManager
from socket_manager import SocketManager
from websocket_server import WebsocketServer

PACKET_SIZE = 1024
SERVER_SOCKET_PORT = 5001
WEBSOCKET_PORT = 7654
SERIAL_PORT = '/dev/tty.usbserial-1420'
BAUD_RATE = 115200

async def main():
    # Initialize the serial port & socket
    uart_manager = UartManager(SERIAL_PORT, BAUD_RATE)
    socket_manager = SocketManager(SERVER_SOCKET_PORT, PACKET_SIZE)
    websocket_server = WebsocketServer(host='localhost', port=WEBSOCKET_PORT)
    net_manager = NetworkManager()
    
    socket_manager.attach_callback(net_manager.callback_socket)
    uart_manager.attach_callback(net_manager.callback_uart)
    net_manager.attach_callback(socket_manager.send_data, uart_manager.send_data, websocket_server.send_data)

    uart_manager.run()
    socket_manager.run()
    websocket_server.run()

    # Start simulating updates
    asyncio.create_task(net_manager.simulate_updates())

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")

if __name__ == "__main__":
    asyncio.run(main())
    print("Server has shut down.")