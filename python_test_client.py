import socket

# Define the server's host and port
SERVER_HOST = '127.0.0.1'  # localhost
SERVER_PORT = 60001        # Port to connect to

# Create a TCP socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    # Connect to the server
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    
    print(f"Connected to server at {SERVER_HOST}:{SERVER_PORT}")
    
    while True:
        # Get input from the user
        message = input("Enter message to send (or 'quit' to exit): ")
        
        if message.lower() == 'quit':
            break
        
        # Send the message to the server
        client_socket.sendall(message.encode())
        
        # Receive response from the server
        response = client_socket.recv(1024)
        
        print("Server response:", response.decode())