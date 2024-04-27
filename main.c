#include "socket.h"
#include <unistd.h>

void cb (char* msg){
    printf("Trigered callback\n");
    printf(" - will process [%s]\n", buffer);

    size_t length = strlen(msg);
    strcpy(msg+length, "-confirmd recived");

    printf(" - for testing, send message back [%s]\n", buffer);
    socket_sent(msg, strlen(msg));
}

int main(){
    // test_sent("My brain blew up");
    // struct init_socket_return_type init;
    Callback cb_func = cb;
    pthread_t tid;
    tid = init_socket(cb_func);
    printf("finished socket init\n");
    

    while (1) {
        printf("main running...\n");
        sleep(1);
    }

    // wait for thread to finish
    if (pthread_join(tid, NULL) != 0) {
        perror("pthread_join");
        return 1;
    }
}
