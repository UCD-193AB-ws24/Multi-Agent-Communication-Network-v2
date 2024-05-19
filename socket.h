#include <stdio.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <pthread.h>
#include <sys/time.h>
#include <sys/types.h>

#define PORT 6001
#define SERVER_PORT 5001
#define SERVER_IP "localhost"
#define BACKLOG 100
#define BUFFER_SIZE 1024


#define SOCKET_OPCODE_LEN 5    // can be veried base on need
#define SOCKET_NODE_ADDR_LEN 2 // need to be 2

typedef void (*Callback) (char*);

// struct init_socket_return_type{
//     int client_fd;
//     pthread_t tid;
// };

int socket_sent(char* message, size_t length, char* response_buffer, size_t buffer_len) ;  /* An example function declaration */
pthread_t init_socket(void(*callback) (char*));
void *listen_thread_func (void* in_args);
int connect_socket(int *socket_fd);