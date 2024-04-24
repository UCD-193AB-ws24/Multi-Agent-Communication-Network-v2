import socket

# Define the host and port you want the server to listen on
HOST = '127.0.0.1'  # localhost
PORT = 60000       # Port to listen on (non-privileged ports are > 1023)

# Create a TCP socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    # Bind the socket to the host and port
    server_socket.bind((HOST, PORT))
    
    # Start listening for incoming connections
    while True:
        server_socket.listen()
        print(f"Server listening on {HOST}:{PORT}")
        
        # Accept incoming connections
        connection, address = server_socket.accept()
        
        with connection:
            print(f"Connected by {address}")
            
            while True:
                # Receive data from the client
                data = connection.recv(1024)
                
                if not data:
                    break
                else:
                    print(f"Received data: {data.decode()}")
                    
                    # Echo back the received data
                    # connection.sendall(data)