#include "socket.h"
#include <unistd.h>

void cb (char* msg){
    printf("Trigered callback\n");
    printf(" - Recive socket message: [%s]\n", msg);

    size_t length = strlen(msg);
    strcpy(msg, "[---]");
    strcpy(msg+length, " - confirmd recived");

    // printf(" - for testing, send message back [%s]\n", msg);
    // socket_sent(msg, strlen(msg));
}

int main(){
    // test_sent("My brain blew up");
    // struct init_socket_return_type init;
    Callback cb_func = cb;
    pthread_t tid;
    char* msg_buffer = (char* ) malloc(BUFFER_SIZE * sizeof(char));
    char* response_buffer = (char* ) malloc(BUFFER_SIZE * sizeof(char));
    strcpy(msg_buffer, "[GET]-Test Message GPS Data");
    // testing send before init
    printf("=> C-API request \"%s\" sent\n", msg_buffer);
    int error_flag = socket_sent(msg_buffer, strlen(msg_buffer), response_buffer, BUFFER_SIZE);
    printf("<= Server response\"%s\" recived\n", response_buffer);
    printf("=================================================\n");
    //
    tid = init_socket(cb_func);
    printf("finished socket init\n");



    

    for(int i = 0; i < 4; i++) {
        printf("=> C-API request \"%s\" sent\n", msg_buffer);
        int error_flag = socket_sent(msg_buffer, strlen(msg_buffer), response_buffer, BUFFER_SIZE);
        printf("<= Server response\"%s\" recived\n", response_buffer);
        printf("=================================================\n");
        sleep(7);
    }

    // wait for thread to finish
    if (pthread_join(tid, NULL) != 0) {
        perror("pthread_join");
        return 1;
    }
}
