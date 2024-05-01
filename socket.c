#include "socket.h"

#define PORT 6001
#define SERVER_PORT 5001
#define SERVER_IP "localhost"
#define BACKLOG 100
#define BUFFER_SIZE 1024

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
        // Receive data from client
        if (read(socket_fd, buffer, BUFFER_SIZE) == -1){
            printf("No Data Readed...\n");
            sleep(1);
            continue;
        }

        callback_func(buffer);
    }

    // // Close sockets
    // close(socket_fd);
}

pthread_t init_socket( Callback cb){ //return socket_fd so it can be closed later
    int socket_fd;
    connect_socket(&socket_fd);
    printf("Read socket connected to server\n");
    socket_sent("[INIT]", 6);

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

int socket_sent(char* message, size_t length) {
    static int send_socket_fd = -1;
    static struct sockaddr_in server_addr;

    if (send_socket_fd == -1) {
        connect_socket(&send_socket_fd);
        printf("Send socket connected to server\n");
    }
    
    
    // Send data to server
    // send(send_socket_fd, message, length, MSG_DONTWAIT);
    int byte_sent = send(send_socket_fd, message, length, 0);
    printf("- Message sent to server [%s]\n", message);
    
    // close(send_socket_fd);
    return byte_sent;
}

void connect_socket(int *socket_fd) {
    int new_socket_fd;
    struct sockaddr_in server_addr;
    *socket_fd = -1; // -1 indicating fail to finish connection
    if ((new_socket_fd = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
        perror("socket creation failed\n");
        return;
    }
    
    // Prepare server address
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    // Convert IPv4 and IPv6 addresses from text to binary form
    if(inet_pton(AF_INET, "127.0.0.1", &server_addr.sin_addr ) == -1) {
        printf("Invalid address\n");
        return;
    }

    *socket_fd = -1;
    // connect network server
    fprintf(stderr, "try to conenct\n");
    if (connect(new_socket_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) == -1) {
        perror("connection failed\n");
        return;
    }
    
    fprintf(stderr, "conencted\n");
    *socket_fd = new_socket_fd;
}