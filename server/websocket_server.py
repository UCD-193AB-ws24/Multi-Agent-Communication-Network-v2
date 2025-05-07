import asyncio
import websockets
import json
import threading

class WebsocketServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.loop = asyncio.new_event_loop()
        self.server = None
        self.running = False
        self.thread = None

    async def handler(self, websocket, path):
        try:
            async for message in websocket:
                print(f" - Received message from client: {message}")
                await websocket.send(message)
        except websockets.exceptions.ConnectionClosedError:
            print("Connection closed")
        except Exception as e:
            print(f"Error: {e}")

    async def start_server(self):
        self.server = await websockets.serve(self.handler, self.host, self.port)
        print(f" - WebSocket server started on ws://{self.host}:{self.port}")
        await self.server.wait_closed()

    def run(self):
        if self.running:
            print("WebSocket server is already running.")
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.thread.start()

    def _run_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.start_server())

    def stop(self):
        if not self.running:
            print("WebSocket server is not running.")
            return

        if self.server:
            self.server.close()
            self.loop.run_until_complete(self.server.wait_closed())
        self.loop.stop()
        self.running = False
        if self.thread:
            self.thread.join()

    async def async_send_data(self, json_data):
        if self.server:
            message = json.dumps(json_data)
            for websocket in self.server.websockets:
                await websocket.send(message)

    def send_data(self, json_data):
        asyncio.run_coroutine_threadsafe(self.async_send_data(json_data), self.loop)