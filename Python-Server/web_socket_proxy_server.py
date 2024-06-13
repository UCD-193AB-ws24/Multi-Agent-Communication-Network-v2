import asyncio
import websockets
import json
import random
import datetime
import sys
import threading
from websocket_server import WebsocketServer
import socket

class TCPServer:
    def __init__(self, host='127.0.0.1', port=8080):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        self.client_socket = None
        self.client_addr = None
        self.connection_thread = threading.Thread(target=self._accept_connection)
        self.connection_thread.start()
        print(f"Server listening on {self.host}:{self.port}")

    def _accept_connection(self):
        self.client_socket, self.client_addr = self.server_socket.accept()
        print('Connected by', self.client_addr)

    def send_message(self, message):
        if self.client_socket:
            try:
                self.client_socket.sendall(message.encode())
                response = self.client_socket.recv(1024)
                print('Received response:', response)
                return response
            except Exception as e:
                print(f"Error sending message: {e}")
        else:
            print("No client connected")

    def close(self):
        if self.client_socket:
            self.client_socket.close()
        self.server_socket.close()

# Example usage
if __name__ == "__main__":
    tcp_server = TCPServer()

    while True:
        msg = input("Enter message to send: ")
        print("=== Sending ====== ")
        data = {
            "type": "networkStatus",
            "status": "nodeStatus",
            "nodes": [
                {"name": "Node-0", "status": "normal"},
                {"name": "Node-1", "status": "normal"}
            ]
        }
        tcp_server.send_message(json.dump(data))
        print("=== Sending ====== ")