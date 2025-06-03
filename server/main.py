from flask import Flask, request
import asyncio
import signal
from network_manager import NetworkManager
from socket_manager import SocketManager
from uart_manager import UartManager
from websocket_server import WebsocketServer
from threading import Thread
import os

PACKET_SIZE = 1024
SERVER_SOCKET_PORT = 5001
WEBSOCKET_PORT = 7654
SERIAL_PORT = "/dev/tty.usbserial-120"
BAUD_RATE = 115200
FLASK_PORT = 5002  # Flask shutdown server port

# Flask app for shutdown
app = Flask(__name__)

@app.route("/shutdown", methods=["POST"])
def shutdown():
    """Properly terminates the Python server."""
    print("Shutdown request received...")

    # Try Werkzeug shutdown method first
    func = request.environ.get("werkzeug.server.shutdown")
    if func:
        print("Shutting down using Werkzeug server shutdown method...")
        func()
        return "Server shutting down...", 200

    # If Werkzeug shutdown fails, use os.kill
    print("Shutting down using os.kill...")
    os.kill(os.getpid(), signal.SIGTERM)
    return "Server shutting down...", 200

def run_flask():
    """Run Flask shutdown server in a separate thread."""
    print("Starting Flask shutdown server on port 5002...")
    app.run(host="0.0.0.0", port=FLASK_PORT, use_reloader=False)

async def main():
    # Start Flask shutdown server in a separate thread
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    await asyncio.sleep(2)  # Give Flask some time to start
    print("Flask should now be running...")

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

if __name__ == "__main__":
    asyncio.run(main())
    print("Server has shut down.")
