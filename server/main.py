from flask import Flask, request
import asyncio
import os
import signal
import sys
from threading import Thread
from network_manager import NetworkManager
from uart_manager import UartManager
from socket_manager import SocketManager
from websocket_server import WebsocketServer

# Configuration
PACKET_SIZE = 1024
SERVER_SOCKET_PORT = 5001
WEBSOCKET_PORT = 7654
SERIAL_PORT = '/dev/tty.usbserial-110'
BAUD_RATE = 115200
FLASK_PORT = 5000  # Flask shutdown server port

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
        func()  # Gracefully shuts down Flask
        return "Server shutting down...", 200

    # If Werkzeug shutdown fails, use os.kill
    print("Shutting down using os.kill...")
    os.kill(os.getpid(), signal.SIGTERM)
    return "Server shutting down...", 200

def run_flask():
    """Run Flask shutdown server in a separate thread."""
    app.run(host="0.0.0.0", port=FLASK_PORT, use_reloader=False)

async def main():
    # Initialize the network components
    uart_manager = UartManager(SERIAL_PORT, BAUD_RATE)
    socket_manager = SocketManager(SERVER_SOCKET_PORT, PACKET_SIZE)
    websocket_server = WebsocketServer(host='localhost', port=WEBSOCKET_PORT)
    net_manager = NetworkManager()
    
    # Attach callbacks
    socket_manager.attach_callback(net_manager.callback_socket)
    uart_manager.attach_callback(net_manager.callback_uart)
    net_manager.attach_callback(socket_manager.send_data, uart_manager.send_data, websocket_server.send_data)

    # Start all network services
    uart_manager.run()
    socket_manager.run()
    websocket_server.run()

    # Start simulating updates
    asyncio.create_task(net_manager.simulate_updates())

    # Start Flask shutdown server in a separate thread
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")

if __name__ == "__main__":
    asyncio.run(main())
    print("Server has shut down.")
