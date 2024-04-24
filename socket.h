#include <stdio.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <pthread.h>

int test_sent(char* msg);  /* An example function declaration */
// int init_socket();
pthread_t init_socket(void(*callback) (char*));
void *listen_thread_func (void* in_args);
void callback_sent (char* msg);

