#include "socket.h"

#define PORT 60001
#define SERVER_PORT 60000
#define SERVER_IP "0.0.0.0"
#define BACKLOG 100

struct listen_thread_arg{
    Callback cb;
    char* argument;
    int server_fd;
};

void *listen_thread_func (void* in_args){
    //unpack thread argument
    struct listen_thread_arg *args= (struct listen_thread_arg*) in_args;
    int server_fd = args->server_fd;
    char* argument = args->argument;
    Callback callback_func = args->cb;
    int client_fd;

    // Listen for incoming connections
    if (listen(server_fd, BACKLOG) == -1) {
        perror("listen failed");
        exit(EXIT_FAILURE);
    }
    printf("Server listening on port %d...\n", PORT);
    struct sockaddr_in client_addr;
    socklen_t client_len = sizeof(client_addr);

        // Accept incoming connections
    if ((client_fd = accept(server_fd, (struct sockaddr *)&client_addr, (socklen_t*)&client_len)) == -1) {
        perror("accept failed");
        exit(EXIT_FAILURE);
    }
    printf("Client connected.\n");
    
    while(1){        
        
        char buffer[1024] = {0};
        // Receive data from client
        if (read(client_fd, buffer, 1024) == -1){
        }

        if(buffer[0] == 0){
          break;
        }
        printf("Client message: %s\n", buffer);
        
        // Send response to client
        char *response = "Hello from server!";
        send(client_fd, response, strlen(response), 0);
        printf("Response sent to client.\n");
        callback_func("hello from callback");
        // test_sent("thread sent");

    }
    // Close sockets
    close(client_fd);
}

pthread_t init_socket( Callback cb){ //return server_fd so it can be closed later
    int server_fd;
    struct sockaddr_in server_addr;
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
        perror("socket creation failed");
        exit(EXIT_FAILURE);
    }
    // Prepare server address
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(PORT);
    
    // Bind socket to address
    if (bind(server_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) == -1) {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }
    
    // spawn a thread here
    pthread_t tid;
    struct listen_thread_arg* args = (struct listen_thread_arg*)malloc(sizeof(struct listen_thread_arg));
    args->cb = cb;
    args->server_fd = server_fd;
    args->argument = "Callback Called\n";
    pthread_create(&tid, NULL, listen_thread_func, (void*)args);
    
    // need to close client_fd outside
    return tid;
}

int test_sent(char* message) {
    int client_fd;
    struct sockaddr_in server_addr;
    char buffer[1024] = {0};
    // char *message = "Hello from client!";
    
    // Create socket
    if ((client_fd = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
        perror("socket creation failed");
        exit(EXIT_FAILURE);
    }
    
    // Prepare server address
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    
    // Convert IP address from string to binary
    if (inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr) == -1) {
        perror("invalid address");
        exit(EXIT_FAILURE);
    }
    
    // Connect to server
    if (connect(client_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) == -1) {
        perror("connection failed");
        exit(EXIT_FAILURE);
    }
    
    printf("Connected to server.\n");
    
    // Send data to server
    send(client_fd, message, strlen(message), 0);
    printf("Message sent to server.\n");
    
    // // Receive response from server
    // read(client_fd, buffer, 1024);
    // printf("Server message: %s\n", buffer);
    
    // Close socket
    close(client_fd);
    
    return 0;
}