#include "socket.h"

struct listen_thread_arg{
    Callback cb;
    int socket_fd;
};

void *listen_thread_func (void* in_args){
    //unpack thread argument
    struct listen_thread_arg *args= (struct listen_thread_arg*) in_args;
    int socket_fd = args->socket_fd;
    Callback callback_func = args->cb;

    printf("Listening on port %d...\n", PORT);
    struct sockaddr_in client_addr;
    socklen_t client_len = sizeof(client_addr);

    
    while(1){        
        char buffer[BUFFER_SIZE] = {0};
        ssize_t byte_read = 0;
        // Receive data from client
        byte_read = read(socket_fd, buffer, BUFFER_SIZE);
        if (byte_read == 0){
            printf("Connection closed...\n");
            sleep(1);
            break;;
        } else if (byte_read == -1) {
            printf("Connection error..\n");
            sleep(1);
            break;;
        }

        callback_func(buffer);
    }

    // // Close sockets
    // close(socket_fd);
}

pthread_t init_socket(Callback cb){ //return socket_fd so it can be closed later
    int socket_fd;
    connect_socket(&socket_fd);
    printf("Read socket connected to server\n");
    // socket_sent("[INIT]", 6); // TB Finish, send message to confirm this is the C-API listen socekt

    // spawn a thread
    pthread_t tid;
    struct listen_thread_arg* args = (struct listen_thread_arg*)malloc(sizeof(struct listen_thread_arg));
    args->cb = cb;
    args->socket_fd = socket_fd;
    pthread_create(&tid, NULL, listen_thread_func, (void*)args);
    
    // need to close socket_fd outside
    // struct  init_socket_return_type ret;
    // ret.socket_fd =socket_fd;
    // ret.tid = tid;
    return tid;
}

// int socket_sent(char* message, size_t length) {
//     static int send_socket_fd = -1;
//     static struct sockaddr_in server_addr;

//     if (send_socket_fd == -1) {
//         connect_socket(&send_socket_fd);
//         printf("Send socket connected to server\n");
//     }
    
    
//     // Send data to server
//     // send(send_socket_fd, message, length, MSG_DONTWAIT);
//     int byte_sent = send(send_socket_fd, message, length, 0);
//     printf("- Message sent to server [%s]\n", message);
    
//     // close(send_socket_fd);
//     return byte_sent;
// }


int socket_sent(char* message, size_t length, char* response_buffer, size_t buffer_len) {
    int socket_fd = -1;

    connect_socket(&socket_fd);
    printf("- Send socket connected to server\n");
    
    // Send data to server
    // send(socket_fd, message, length, MSG_DONTWAIT);
    int byte_sent = send(socket_fd, message, length, 0);
    printf("=> Message sent to server [%s]\n", message);

    // ==== timeout for response ====
    struct timeval timeout;
    timeout.tv_sec = 5;  // 5 seconds timeout
    timeout.tv_usec = 0;

    fd_set readfds;
    FD_ZERO(&readfds);
    FD_SET(socket_fd, &readfds); // Add socket_fd to the monitor set

    int ready = select(socket_fd + 1, &readfds, NULL, NULL, &timeout);
    printf("- wating on response...\n");
     if (ready == -1) {
        perror("Select error");
        exit(EXIT_FAILURE);
    } else if (ready == 0) {
        printf("Timeout occurred\n");
        exit(EXIT_FAILURE);
    }

    // Check if sockfd is ready for reading
        // Data is available for reading
    int bytes_received = recv(socket_fd, response_buffer, buffer_len, 0);
    if (bytes_received == -1) {
        perror("Receive error");
        exit(EXIT_FAILURE);
    } else if (bytes_received == 0) {
        printf("Connection closed from server\n");
        exit(EXIT_SUCCESS);
    } else {
        // Data received successfully
        printf("<= Received %d bytes: %s\n", bytes_received, response_buffer);
    }
    
    close(socket_fd);
    return 1; // for success
}

int connect_socket(int *socket_fd) {
    static struct sockaddr_in server_addr;
    static int server_addr_initialized = -1;
    int new_socket_fd;
    
    if (server_addr_initialized == -1) {
        // Prepare server address
        server_addr.sin_family = AF_INET;
        server_addr.sin_port = htons(SERVER_PORT);
        // Convert IPv4 and IPv6 addresses from text to binary form
        if(inet_pton(AF_INET, "127.0.0.1", &server_addr.sin_addr ) == -1) {
            printf("Invalid server address\n");
            return -1;
        }
        server_addr_initialized = 1;
    }
        

    *socket_fd = -1; // -1 indicating fail to finish connection
    if ((new_socket_fd = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
        perror("socket creation failed\n");
        return -1;
    }
    

    *socket_fd = -1;
    // connect network server
    fprintf(stderr, "try to conenct\n");
    if (connect(new_socket_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) == -1) {
        perror("connection failed\n");
        return -1;
    }
    
    fprintf(stderr, "conencted\n");
    *socket_fd = new_socket_fd;
    return 0;
}