#include "socket.h"
// version 1, all temporary
/*
things I am not sure:
not sure how exactly notifier predefined callback will work
not sure how exactly will client's request function gets the response
 */ 

#define BUFFER_SIZE 1024

int cb_num = 6;
int cb_max = 6;

typedef struct node_data{
    int data_type_id;
    char* data;
}node_data;

typedef struct node{
    node_data data;
    int status;
}edge_node;

// Maybe don't pass the callback function in the listener thread, but store it as global variable a malloc in heap?
// should the table be or node id pair with node itsef?
typedef struct node_table{
    int node_addr;
    int node_id;
}node_table;

// callback functions as a array of function pointer
Callback *cb_array;

int wait_for_response(char* buffer, int meg_id) {
    // write the data into buffer when message comes back

    if (1==1) {
        // if has response for meg_id
        // copy response to buffer
        return 0;
    }

    return -1; // no response
}

edge_node Get_network_info(){
    char* msg_buffer = (char* ) malloc(BUFFER_SIZE*sizeof(char));
    int msg_id = socket_sent("network_info request", strlen("network_info request"));

    if (wait_for_response(msg_buffer, msg_id) == -1) {
        // no response back
    }
}

//start the network tread and start the network 
pthread_t Network_API_Initalization(Callback client_defined_cb){
    construct_callback_function_list();
    pthread_t tid;
    tid = init_socket(client_defined_cb);
    return tid;
}

int send_custom_message(int op_code, char* message, size_t length){
    // might change to return message id
    return socket_sent(message, length);
}

size_t common_request_message_constructer(char* msg_buffer, int edge_node_id, int data_type_id){
    //craft message;
    strcpy(msg_buffer, "reuquest message place holder");
    return strlen("reuquest message place holder");
}

node_data Get_node_data(int edge_node_id, int data_type_id){
    char* msg_buffer = (char* ) malloc(BUFFER_SIZE*sizeof(char));
    size_t length = common_request_message_constructer(msg_buffer, edge_node_id, data_type_id);
    int msg_id = socket_sent(msg_buffer, length);

    if (wait_for_response(msg_buffer, msg_id) == -1) {
        // no response back
    }
    //some how gets response. 
}
