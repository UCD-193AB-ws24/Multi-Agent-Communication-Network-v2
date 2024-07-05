import asyncio
import websockets
import json
import random
import time
import threading
from websocket_server import WebsocketServer
import socket

class Web_Socket_Manager:
    def __init__(self, host='127.0.0.1', port=8080):
        self.host = host
        self.port = port
        self.client = None
        self.server = None
        self.loop = asyncio.new_event_loop()
        self.server_thread = threading.Thread(target=self.start_loop, args=(self.loop,))
        self.server_thread.start()

    def start_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    async def register_client(self, websocket):
        self.client = websocket
        try:
            await websocket.wait_closed()
        finally:
            self.client = None

    async def async_send_to_web(self, json_data):
        print(self.client)
        print(json_data)
        if self.client:
            message = json.dumps(json_data)
            await self.client.send(message)

    def send_to_web(self, json_data):
        print(" === send data right now")
        asyncio.run_coroutine_threadsafe(self.async_send_to_web(json_data), self.loop)

    async def start_server(self, websocket, path):
        await self.register_client(websocket)

    async def run_server(self):
        self.server = await websockets.serve(self.start_server, self.host, self.port)
        await self.server.wait_closed()

    def run(self):
        asyncio.run_coroutine_threadsafe(self.run_server(), self.loop)
        print("=== Web socket (server) running ===")

    async def async_stop(self):
        print("Stopping server and closing the client.")
        if self.client:
            await self.client.close()
        self.server.close()
        await self.server.wait_closed()

    def stop(self):
        asyncio.run_coroutine_threadsafe(self.async_stop(), self.loop)

# Dummy JSON data
dummy_data = {
    "type": "networkStatus",
    "status": "nodeStatus",
    "nodes": [
        {"name": "Node-0", "status": random.choice(["normal", "error"])},
        {"name": "Node-1", "status": random.choice(["normal", "error"])}
    ]
}

# # Create an instance of Web_Socket_Manager
# ws_manager = Web_Socket_Manager(port=7654)
# ws_manager.run()

# # Simulate sending data after some time
# time.sleep(4)
# ws_manager.send_to_web(dummy_data)

# # Automatically stop the server after some time (e.g., 10 seconds)
# time.sleep(10)
# ws_manager.stop()
