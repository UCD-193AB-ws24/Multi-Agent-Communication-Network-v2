#include "socket.h"
#include <unistd.h>

size_t craft_response(char* response, char* addr){
    printf("crafting\n");
    size_t msg_len = 0;
    char* op_code = "[RES]";
    char* data = "this is a response from client";
    strcpy(response, op_code);
    msg_len += strlen(op_code);
    msg_len += 2;
    memcpy(response+strlen(op_code), addr, 2);
    memcpy(response+strlen(op_code)+ 2, data, strlen(data));
    msg_len += strlen(data);
    response[msg_len]='\0';
    return msg_len;
}

void cb (char* msg){

    // response code
    printf("callback called\n");
    char op[6]; 
    char addr[2];
    memcpy(op, msg, 5);
    op[5] = '\0';
    if (!strcmp(op, "[REQ]")){
        char addr[2];
        memcpy(addr, msg+5, 2);
        // need msg length
        
        char len;
        memcpy(&len, msg+7,1);
        printf("len %d\n", len);
        char data[len];
        memcpy (data, msg+8, len);
        printf("data:%s\n",data);
        char * response = (char* ) malloc(BUFFER_SIZE * sizeof(char));
        size_t msg_len= craft_response(response, addr);
        printf("%ld\n", msg_len);
        socket_sent( response, msg_len, NULL, 0 );
    }
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

    // fake uartmessage
    strcpy(msg_buffer, "<Q>");
    u_int16_t node_addr = 0x0500;
    memcpy(msg_buffer + strlen("<Q>"), &node_addr, 2);
    size_t msg_len = strlen("<Q>") + 2;
    char *payload = "this is request";
    memcpy(msg_buffer + msg_len, payload, strlen(payload));
    msg_len += strlen(payload);
    msg_buffer[msg_len] = '\0';
    printf("%s\n",msg_buffer);
    socket_sent(msg_buffer, msg_len, NULL, 0);


    // wait for thread to finish
    if (pthread_join(tid, NULL) != 0) {
        perror("pthread_join");
        return 1;
    }
}
