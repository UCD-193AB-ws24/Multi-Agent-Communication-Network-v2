import asyncio
import signal
from network_manager import NetworkManager
from socket_manager import SocketManager
from uart_manager import UartManager
from websocket_server import WebsocketServer

PACKET_SIZE = 1024
SERVER_SOCKET_PORT = 5001
WEBSOCKET_PORT = 7654
SERIAL_PORT = "/dev/tty.usbserial-1430"
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
    
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[MAIN] KeyboardInterrupt caught outside event loop.")