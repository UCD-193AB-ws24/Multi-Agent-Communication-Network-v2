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
    tid = init_socket(cb_func);
    printf("finished socket init\n");
    char* msg_buffer = (char* ) malloc(BUFFER_SIZE * sizeof(char));
    char* response_buffer = (char* ) malloc(BUFFER_SIZE * sizeof(char));
    response_buffer[30] = '\0';


    strcpy(msg_buffer, "[GET]GPS");
    u_int8_t node_addr = 0x05;
    memcpy(msg_buffer + strlen("[GET]GPS"), &node_addr, 1);
    size_t msg_len = strlen("[GET]GPS") + 1;
    msg_buffer[msg_len] = '\0';

    while (1) {
        printf("=> C-API request \"%s\" sent\n", msg_buffer);
        int error_flag = socket_sent(msg_buffer, msg_len, response_buffer, BUFFER_SIZE);
        printf("<= Server response\"%s\" recived\n", response_buffer);
        
        char* byte_itr = response_buffer + 4;
        int8_t data_len = (int8_t)byte_itr[0]; // will be 6
        byte_itr += 1;

        int8_t node_addr = (int8_t)byte_itr[0]; // will be 1
        byte_itr += 1;

        int16_t n1 = (int16_t)(byte_itr[1] << 8 | byte_itr[0]);
        byte_itr += 2;
        int16_t n2 = (int16_t)(byte_itr[1] << 8 | byte_itr[0]);
        byte_itr += 2;
        int16_t n3 = (int16_t)(byte_itr[1] << 8 | byte_itr[0]);
        byte_itr += 2;
        fprintf(stderr, " * Node-%d GPS:%d bytes (%d,%d,%d)\n", node_addr, data_len, n1, n2, n3);
        
        sleep(2);
    }

    // wait for thread to finish
    if (pthread_join(tid, NULL) != 0) {
        perror("pthread_join");
        return 1;
    }
}
