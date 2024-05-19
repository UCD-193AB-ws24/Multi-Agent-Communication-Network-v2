#include "socket.h"
#include <unistd.h>
#include <stdint.h>

int edge_robot_request_handler(uint16_t node_addr) {
    // for demo purpose, accept one request and reject one request
    static int avaiable  = 1;

    printf("[Request] robot recived from edge %hu, avaiablilty %d", node_addr, avaiable);

    if (avaiable > 0) {
        avaiable--;
        return 1;
    } else {
        avaiable++; // fake refil on robot availability
        return 0;
    }
}

void socket_message_callback(char* socket_msg) {
    printf("\n=== socket callback trigered === \n");
    printf("\nsocket message \'%.12s\'\n", socket_msg);

    int opcode_num = getOpcodeNum(socket_msg);
    uint16_t node_addr = getNodeAddr(socket_msg + SOCKET_OPCODE_LEN);
    char* payload = socket_msg + SOCKET_OPCODE_LEN + SOCKET_NODE_ADDR_LEN;
    printf("opcode_num: %d, node_addr: %hu\n", opcode_num, node_addr);

    switch (opcode_num)
    {
    case -1:
        fprintf(stderr, "Error, socket recived unkown opcode \'%.5s\'\n", socket_msg);
        break;
    case 0: // [REQ], request from edge device
        // Request payload includes, 1_byte_type_name_len|n_byte_type_name
        // uint8_t length = (uint8_t)payload[0];  // forgoted to encode in ardunion for demo
        char* request_type = payload; // payload + 1;

        printf("  * [REQ] - request\n");
        if (strncmp(request_type, "Robot", 5) == 0) {
            printf("  * [REQ] - Robot request\n");
            char *request_response = (char* ) malloc(BUFFER_SIZE * sizeof(char));
            char response_message = '-';

            if (edge_robot_request_handler(node_addr) == 1) {
                response_message = 'A'; // accept the robot request
            } else {
                response_message = 'R'; // reject the robot request
            }

            size_t response_len = socket_craft_message_example(request_response, BUFFER_SIZE, "[REQ]", node_addr, &response_message, 1);
            fprintf(stderr, "Sendning request_response... \'%.6s\'\n", request_response);
            socket_sent(request_response, response_len, NULL, 0); // "NULL, 0" means no need for response
            fprintf(stderr, "Sended request_response\n\n");

            free(request_response);
        }
        break;

    case 1: // EMPTY, empty opcode
        break;
    default:
        break;
    }
}

void Data_Request_example(uint16_t node_addr, char* data_type, size_t data_type_len) {
    char* msg_buffer = (char* ) malloc(BUFFER_SIZE * sizeof(char));
    char* response_buffer = (char* ) malloc(BUFFER_SIZE * sizeof(char));
    response_buffer[30] = '\0'; // for testing log printing

    /****************** craft the get_data_message ******************/
    size_t msg_len = socket_craft_message_example(msg_buffer, BUFFER_SIZE, "[GET]", node_addr, data_type, data_type_len);
    msg_buffer[msg_len] = '\0';  // for testing log printing

    printf("=> C-API request \"%s\" sent\n", msg_buffer);
    int error_flag = socket_sent(msg_buffer, msg_len, response_buffer, BUFFER_SIZE);
    printf("<= Server response\"%s\" recived\n", response_buffer);
    // response_buffer contains only response to socket_sent, not socket opcode in it
    
    // S|data_type|data_length_byte|size_n|node_addr/index_0|data_0|...|node_addr/index_n|data_n
    // F|error_message_length|error_message
    char* byte_itr = response_buffer;
    
    if (*byte_itr != 'S') {
        // failed
        printf("Failed to get data");
        sleep(2);
        return;
    }

    /****************** example decodeing message******************/
    // format of data agreed with arduion-c-api side
    // what ever format sended from arduion will get returned from socket
    byte_itr = response_buffer + strlen("GPS") + 1;
    int8_t data_len = (int8_t)byte_itr[0]; // will be 6
    byte_itr += 1;

    int8_t node_amount = (int8_t)byte_itr[0]; // will be 1
    byte_itr += 1;

    int16_t n1 = (int16_t)(byte_itr[1] << 8 | byte_itr[0]);
    byte_itr += 2;
    int16_t n2 = (int16_t)(byte_itr[1] << 8 | byte_itr[0]);
    byte_itr += 2;
    int16_t n3 = (int16_t)(byte_itr[1] << 8 | byte_itr[0]);
    byte_itr += 2;
    fprintf(stderr, " * Node-%d GPS:%d bytes (%d,%d,%d)\n", node_addr, data_len, n1, n2, n3);

    free(msg_buffer);
    free(response_buffer);
}

int main(){
    // test_sent("My brain blew up");
    // struct init_socket_return_type init;
    pthread_t tid;
    tid = init_socket(socket_message_callback);
    printf("finished socket init\n");


    uint16_t node_addr = 5; // first node connected
    while (1) {
        Data_Request_example(node_addr, "GPS", 3);
        printf("\n");
        sleep(10);
    }


    // wait for thread to finish
    if (pthread_join(tid, NULL) != 0) {
        perror("pthread_join");
        return 1;
    }
}
