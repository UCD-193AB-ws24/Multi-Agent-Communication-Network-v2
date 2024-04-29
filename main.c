#include "socket.h"
#include <unistd.h>

void cb (char* msg){
    printf("Trigered callback\n");
    printf(" - Recive socket message: [%s]\n", msg);

    size_t length = strlen(msg);
    strcpy(msg, "[---]");
    strcpy(msg+length, " - confirmd recived");

    printf(" - for testing, send message back [%s]\n", msg);
    socket_sent(msg, strlen(msg));
}

int main(){
    // test_sent("My brain blew up");
    // struct init_socket_return_type init;
    Callback cb_func = cb;
    pthread_t tid;
    tid = init_socket(cb_func);
    printf("finished socket init\n");
    char* buffer = (char* ) malloc(1024*sizeof(char));


    strcpy(buffer, "[GET] GPS Data");

    while (1) {
        printf("main request data\n");
        socket_sent(buffer, strlen(buffer));
        sleep(1);
    }

    // wait for thread to finish
    if (pthread_join(tid, NULL) != 0) {
        perror("pthread_join");
        return 1;
    }
}
