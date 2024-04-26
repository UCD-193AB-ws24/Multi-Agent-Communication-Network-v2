#include <stdio.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <pthread.h>

typedef void (*Callback) (char*);

// struct init_socket_return_type{
//     int client_fd;
//     pthread_t tid;
// };

int test_sent(char* msg);  /* An example function declaration */
pthread_t init_socket(void(*callback) (char*));
void *listen_thread_func (void* in_args);
void callback_sent (char* msg);

