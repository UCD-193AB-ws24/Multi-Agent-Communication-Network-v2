#include "socket.h"
#include <unistd.h>
#include <stdint.h>

#define socket_op_amount 2

const char scoket_opcode[socket_op_amount][SOCKET_OPCODE_LEN + 1] = { // +1 for '\0'
  "[REQ]", "EMPTY"
};

int edge_robot_request_handler(uint16_t node_addr) {
    // for demo purpose, accept one request and reject one request
    static int avaiable  = 1;

    if (avaiable > 0) {
        avaiable--;
        return 1;
    } else {
        avaiable++; // fake refil on robot availability
        return 0;
    }
}

void socket_message_callback(char* socket_msg) {
    printf("socket callback trigered\n");
    int opcode_num = getOpcodeNum(socket_msg);
    uint16_t node_addr = getNodeAddr(socket_msg + SOCKET_OPCODE_LEN);
    char* payload = socket_msg + SOCKET_OPCODE_LEN + SOCKET_NODE_ADDR_LEN;

    switch (opcode_num)
    {
    case -1:
        fprintf(stderr, "Error, socket recived unkown opcode \'%.5s\'\n", socket_msg);
        break;
    case 0: // [REQ], request from edge device
        // Request payload includes, 1_byte_type_name_len|n_byte_type_name
        uint8_t length = (uint8_t)payload[0];
        char* request_type = payload + 1;

        if (strncmp(request_type, "Robot", 6) == 0) {
            char *request_response = (char* ) malloc(BUFFER_SIZE * sizeof(char));
            char response_message = '-';

            if (edge_robot_request_handler(node_addr) == 1) {
                response_message = 'A'; // accept the robot request
            } else {
                response_message = 'R'; // reject the robot request
            }

            size_t response_len = socket_craft_message_example(request_response, BUFFER_SIZE, "[REQ]", node_addr, &response_message, 1);
            socket_sent(request_response, response_len, NULL, 0); // "NULL, 0" means no need for response

            free(request_response);
        }
        break;

    case 1: // EMPTY, empty opcode
        break;
    default:
        break;
    }
}

int main(){
    // test_sent("My brain blew up");
    // struct init_socket_return_type init;
    pthread_t tid;
    tid = init_socket(socket_message_callback);
    printf("finished socket init\n");
    char* msg_buffer = (char* ) malloc(BUFFER_SIZE * sizeof(char));
    char* response_buffer = (char* ) malloc(BUFFER_SIZE * sizeof(char));
    response_buffer[30] = '\0'; // for testing log printing


    uint16_t node_addr = 5; // first node connected
    size_t msg_len = socket_craft_message_example(msg_buffer, BUFFER_SIZE, "[GET]", node_addr, "GPS", 3);
    msg_buffer[msg_len] = '\0';  // for testing log printing

    while (1) {
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
            continue;
        }

        // example decodeing, format of data agreed with arduion-c-api side
        char* byte_itr = response_buffer + strlen("GPS") + 1;
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
        
        sleep(2);
    }


    // wait for thread to finish
    if (pthread_join(tid, NULL) != 0) {
        perror("pthread_join");
        return 1;
    }
}
