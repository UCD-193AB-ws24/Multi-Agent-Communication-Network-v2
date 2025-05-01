import signal
import socket
import threading

class SocketManager:
    def __init__(self, server_listen_port, packet_size):
        self.packet_size = packet_size
        self.server_listen_port = server_listen_port
        self.server_socket = None
        self.server_listen_thread = None
        self.send_socket = None
        self.send_address = None
        self.callback_func = None
        self.is_connected = False
        self.initialize_socket()
        signal.signal(signal.SIGINT, self.SIGINT_handler)

    def log(self, level, message):
        print(f"[SOCKET][{level}]  - {message}")

    def SIGINT_handler(self, signum, frame):
        if self.send_socket: self.send_socket.close()
        if self.server_socket: self.server_socket.close()

    def initialize_socket(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("localhost", self.server_listen_port))
        self.server_socket.settimeout(None)
        self.log("INFO", f"Socket initialized on port {self.server_listen_port}")

    def run(self):
        self.socket_thread = threading.Thread(target=self.server_listening_thread, daemon=True)
        self.socket_thread.start()

    def attach_callback(self, callback_func):
        self.callback_func = callback_func

    def connect_send_socket(self):
        self.server_socket.listen(1)
        while not self.is_connected:
            send_socket, send_address = self.server_socket.accept()
            data = send_socket.recv(self.packet_size)
            self.log("RECEIVE", f"Handshake from {send_address}: {data}")
            if data != b"[syn]\x00":
                send_socket.send(b"[err]-listen_socket_disconnected")
                send_socket.close()
            else:
                send_socket.send(b"[ack]\x00")
                self.is_connected = True
                self.log("CONNECT", f"Handshake accepted from {send_address}")
        self.send_socket = send_socket
        self.send_address = send_address
        self.log("CONNECT", f"Send socket established with {send_address}")

    def server_listening_thread(self):
        self.log("THREAD", "Starting server socket listening thread")
        self.connect_send_socket()
        self.server_socket.listen(5)
        try:
            while True:
                if not self.is_connected:
                    self.log("WARN", "Reconnecting...")
                    self.connect_send_socket()
                client_socket, address = self.server_socket.accept()
                self.log("CONNECT", f"New connection from {address}")
                threading.Thread(target=self.socket_handler, args=(client_socket,), daemon=True).start()
        except Exception as e:
            self.log("ERROR", f"Exception: {e}")
        finally:
            if self.server_socket: self.server_socket.close()
            if self.send_socket: self.send_socket.close()

    def socket_handler(self, client_socket):
        try:
            data = client_socket.recv(self.packet_size)
            if data == b"[syn]\x00":
                self.is_connected = False
                client_socket.send(b"[err]-listen_socket_disconnected")
                client_socket.close()
                return
            
            response_bytes = self.callback_func(data)
            client_socket.send(response_bytes)
            client_socket.close()
        except Exception as e:
            self.log("ERROR", f"Socket handler error: {e}")
        finally:
            client_socket.close()

    def send_data(self, data):
        if self.send_socket:
            try:
                self.send_socket.sendall(data)
                self.log("SEND", f"Sent data: {data}")
                return b"S"
            except socket.error as e:
                self.is_connected = False
                self.send_socket.close()
                return b"F" + f"Socket error: {str(e)}".encode()
        else:
            self.log("ERROR", "No socket connected")
            return b"F" + b"No socket connected"
