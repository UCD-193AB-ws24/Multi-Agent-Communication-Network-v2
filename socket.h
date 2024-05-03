#include <stdio.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <pthread.h>
#include <sys/time.h>
#include <sys/types.h>


typedef void (*Callback) (char*);

// struct init_socket_return_type{
//     int client_fd;
//     pthread_t tid;
// };

int socket_sent(char* msg, size_t length);  /* An example function declaration */
pthread_t init_socket(void(*callback) (char*));
void *listen_thread_func (void* in_args);
void connect_socket(int *socket_fd);