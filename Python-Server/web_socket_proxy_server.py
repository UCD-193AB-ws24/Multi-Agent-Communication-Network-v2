import asyncio
import websockets
import json
import random
import datetime
import sys

class Web_Socket_Manager:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.connected_clients = set()
        self.server = None

    async def register_client(self, websocket):
        self.connected_clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            self.connected_clients.remove(websocket)

    async def async_send_to_web(self, json_data):
        if self.connected_clients:  # Ensure there are connected clients
            message = json.dumps(json_data)
            await asyncio.wait([client.send(message) for client in self.connected_clients])

    def send_to_web(self, json_data):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.async_send_to_web(json_data))
        
    async def start_server(self, websocket, path):
        await self.register_client(websocket)

    async def run_server(self):
        self.server = await websockets.serve(self.start_server, self.host, self.port)
        await self.server.wait_closed()

    def run(self):
        # Start the WebSocket server
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        new_loop.run_until_complete(self.run_server())
