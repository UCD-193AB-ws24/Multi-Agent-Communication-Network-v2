#include "socket.h"
#include <unistd.h>
#include <stdint.h>

#define socket_op_amount 2

const char scoket_opcode[socket_op_amount][SOCKET_OPCODE_LEN + 1] = { // +1 for '\0'
  "[REQ]", "EMPTY"
};

int getOpcodeNum(char* opcode) {
    for (int i = 0; i < socket_op_amount; ++i) {
        if (strncmp(opcode, scoket_opcode[i], strlen(scoket_opcode[i])) == 0) {
            return i;
        }
    }

    return -1;
}

uint16_t getNodeAddr(const char* data) {
    // Decode the node address
    uint8_t byte1 = (uint8_t)data[0];
    uint8_t byte2 = (uint8_t)data[1];
    
    // Combine the two bytes into a single uint16_t value
    uint16_t combined = ((uint16_t)byte1 << 8) | (uint16_t)byte2;
    
    // Convert the combined value from network byte order to host byte order
    // Network to Host Short, ensures the endianess on both side
    uint16_t host_value = ntohs(combined);
    
    return host_value;
}

size_t socket_craft_message_example(char* buffer, size_t buffer_len, char* socket_opcode, uint16_t node_addr, char* payload, size_t payload_len){
    printf("crafting socket message\n");
    char* buffer_itr = buffer;
    size_t byte_count = 0;
    
    memcpy(buffer, socket_opcode, SOCKET_OPCODE_LEN);
    buffer_itr += SOCKET_OPCODE_LEN;
    byte_count += SOCKET_OPCODE_LEN;

    node_addr = htos(node_addr); // Convert to network byte order

    memcpy(buffer, &node_addr, SOCKET_NODE_ADDR_LEN);
    buffer_itr += SOCKET_NODE_ADDR_LEN;
    byte_count += SOCKET_NODE_ADDR_LEN;

    
    memcpy(buffer, payload, payload_len);
    buffer_itr += payload_len;
    byte_count += payload_len;

    return byte_count;
}

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
