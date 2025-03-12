import socket
import threading
from datetime import datetime
import signal

class SocketManager():
    def __init__(self, server_listen_port, packet_size):
        self.packet_size = packet_size
        self.server_listen_port = server_listen_port
        self.server_socket = None             # Listen for all socket connection
        self.server_listen_thread = None
        self.send_socket = None               # The Main communication Socket for python sending to C-API
        self.send_address = None
        self.callback_func = None
        self.is_connected = False
        self.initialize_socket()
        signal.signal(signal.SIGINT, self.SIGINT_handler)

    def SIGINT_handler(self, signum, frame):
        self.send_socket.close()
        self.server_socket.close()
        exit(0)
        
    def initialize_socket(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', self.server_listen_port))
        self.server_socket.settimeout(None)  # accept_connectiondont timeout when waiting for response

    def run(self):
        self.socket_thread = threading.Thread(target=self.server_listening_thread, args=(), daemon=True)
        self.socket_thread.start()
    
    def attach_callback(self, callback_func):
        self.callback_func = callback_func
                
    def connect_send_socket(self):
        self.server_socket.listen(1)

        # Handshake
        while self.is_connected is False:
            send_socket, send_address = self.server_socket.accept()
            data = send_socket.recv(self.packet_size)
            print(f"{datetime.now()} - Received handshake {data} from {send_address}")
            if data != b'[syn]\x00':
                send_socket.send(b'[err]-listen_socket_disconnected')
                send_socket.close()
            else:
                print(f"{datetime.now()} - Received handshake from {send_address}")
                send_socket.send(b'[ack]\x00')
                self.is_connected = True

        self.send_socket = send_socket
        self.send_address = send_address
        print(f"{datetime.now()} - Connected with send: {send_address}")
        
    def server_listening_thread(self):
        print(f"{datetime.now()} - Starting server-socket listening thread")
        self.connect_send_socket()
        
        # listen to socket sonnection for C-API data/message request
        self.server_socket.listen(5)
        print(f"{datetime.now()} - Listening on 'localhost':{self.server_listen_port} for C-API socket connection")
        try:
            while True:
                #------TB Review : reconnection----------------
                if(self.is_connected == False):
                    print(" - Reconnecting...")
                    self.connect_send_socket()
                #----------------------------------------------
                client_socket, address = self.server_socket.accept()
                print(f"{datetime.now()} - Requested connection from C-API in {address} has been established.") # [Testing Log]
                
                request_handler_thread = threading.Thread(target=self.socket_handler, args=(client_socket,))
                request_handler_thread.start()
        except Exception as e:
            print('Exception in server-socket listening thread:', e)
        except KeyboardInterrupt:
            print("KeyboardInterrupt")
        finally:
            if self.server_socket != None:
                self.server_socket.close()
            if self.send_socket != None:
                self.send_socket.close()
            pass
                

    def socket_handler(self, client_socket):
        # print("Starting new C-API socket request thread")  # [Testing Log]

        # read the request from C-API from socket
        data = client_socket.recv(self.packet_size)
        #if the socket is trying to handshake meaning client was disconnected
        if(data == b'[syn]\x00'):
            self.is_connected = False
            client_socket.send(b'[err]-listen_socket_disconnected')
            client_socket.close()
            return
        # print("Received Request:", data.decode())

        # pass data to Net_Manager's function to handler and return the response
        response_bytes = self.callback_func(data)
        client_socket.send(response_bytes)
        client_socket.close()
        
    def send_data(self, data): # -------------------- TB Finish --------------------------
        if self.send_socket != None:
            # socket.sento(bytes, addr)
            try:
                self.send_socket.sendall(data)
            except socket.error as e:
                err_no = e.errno
                error_str = e.strerror
                if(err_no == 32 or err_no == 104 or err_no == 111):
                    print("Client socket disconnected")
                    self.send_socket.close()
                    self.is_connected = False
                    return b'F' + "Client socket disconnected".encode()
                if err_no == 110:
                    print("Connection timeout")
                    return b'F' + "Connection timeout".encode()
        else:
            print("No socket connected")
            return b'F' + "No socket connected".encode()
            # implment attemps of reconnection
        
        return b'S'