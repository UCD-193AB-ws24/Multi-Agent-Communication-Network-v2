import asyncio
import websockets
import json
import random
import datetime
import sys
import threading

class Web_Socket_Manager:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.connected_clients = set()
        self.server = None

    async def register_client(self, websocket):
        self.connected_clients.add(websocket)
        print("=== register_client === ")
        try:
            await websocket.wait_closed()
        finally:
            self.connected_clients.remove(websocket)
        print("=== done register_client === ")

    async def async_send_to_web(self, json_data):
        print("=== Sending 3 === ")
        if self.connected_clients:  # Ensure there are connected clients
            print("=== Sending  3-- === ")
            message = json.dumps(json_data)
            await asyncio.wait([client.send(message) for client in self.connected_clients])

    def send_to_web(self, json_data):
        print("=== Sending 1 === ")
        loop = asyncio.get_event_loop()
        print("=== Sending 2 === ")
        loop.run_until_complete(self.async_send_to_web(json_data))
        print("=== Sending 4 === ")
        
    async def start_server(self, websocket, path):
        await self.register_client(websocket)

    async def run_server(self):
        self.server = await websockets.serve(self.start_server, self.host, self.port)
        await self.server.wait_closed()

    def run(self):
        # Start the WebSocket server
        
        def start_loop(loop):
            asyncio.set_event_loop(loop)
            loop.run_forever()

        new_loop = asyncio.new_event_loop()
        t = threading.Thread(target=start_loop, args=(new_loop,))
        t.start()

        asyncio.run_coroutine_threadsafe(self.run_server(), new_loop)
        print("=== Web socket (server) running === ")
