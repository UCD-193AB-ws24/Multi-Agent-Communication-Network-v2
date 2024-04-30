#include "socket.h"
// version 1, all temporary
/*
things I am not sure:
not sure how exactly notifier predefined callback will work
not sure how exactly will client's request function gets the response
 */ 
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
    edge_node node;
    int node_id;
}node_table;

// callback functions as a array of function pointer
Callback *cb_array;
/*
from the doc
-Robot Request
Send_robot_availability 
pack this into API for easier use, pre-defined message type
-Idle-Request
Maybe? Need to confirm if they want something like this to stop using that Node’s GPS
-Node-Offline-Notification
Notify the main control when there is some node offline
-Battery-Replacement-Request
Maybe
-Emergency-Notification
Alarm an emergency
-Custom-Message
Receive a custom message to central software


*/
// default callback functions
//==========================

// not sure how exactly notifier work
void robot_request_notifier(int node_id){
    //notifies the client 
}

void idle_request_notifier(int node_id){
    //notifies the client 
}

void node_offline_request_notifier(int node_id){
    //notifies the client
}

void battery_replacement_request_notifier(int node_id){
    //does something
}

void emergency_notification_notifier(int node_id, char message[]){
    // does something

}

void custom_message_from_edge_notifier(int node_id, char message[]){
    // does something
}
//=========================



//internal helper function
//===================================

char* common_request_message_constructer(int edge_node_id, int data_type_id){
    //craft message;
    return "reuquest message place holder";
}

// parse message from listening queue?
int parse_op_code(char* buff){
    //to do: parse opcode
    return 0;//place holder
}

// attach a new callback and returns the callback's index in the callback array that's also the opcode
int add_callback_function(Callback new_cb){
    cb_num += 1;
    if(cb_num > cb_max){
        Callback *new_cb_array = realloc( cb_array, cb_max * sizeof(Callback));
        if (new_cb_array == NULL) {
            printf("Memory reallocation failed\n");
            // Handle error: Don't change global_array
            return -1;
        }
        new_cb_array[cb_num - 1] = new_cb;
        free(cb_array);
        cb_array = new_cb_array;
    }
    else{
        cb_array[cb_num] = new_cb;
    }
    //return op code
    return cb_num - 1;
}

void construct_callback_function_list(){
    cb_array = malloc(cb_num * sizeof(Callback));
    if (cb_array == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        return 1;
    }

    // default callback functions to the array, based on the doc
    cb_array[0] = robot_request_notifier;
    cb_array[1] = idle_request_notifier;
    cb_array[2] = node_offline_request_notifier;
    cb_array[3] = battery_replacement_request_notifier;
    cb_array[4] = emergency_notification_notifier;
    cb_array[5] = custom_message_from_edge_notifier;
}
//================================


// whenever a inbound traffic received by the listener thread this is called, this should save the inbound message or parse it
void default_callback_function(char message){
    // parse here
    int op_code = parse_op_code(message);
    Callback cb = cb_array[op_code];
    cb();
    // or just keep everything in a container that container is shared between thread.
}

edge_node Get_network_info(){
    socket_sent("network_info request");
    // busy waiting? check for listning queue?
}

//start the network tread and start the network 
pthread_t Network_API_Initalization(){
    construct_callback_function_list();
    pthread_t tid;
    tid = init_socket(robot_request_notifier); // should pass in a cb_array, just a place holder for now
    return tid;
}

void send_custom_message(int op_code, char* message){
    socket_sent(message, strlen(message));
    // some how gets response.
}

node_data Get_node_data(int edge_node_id, int data_type_id){
    char* message = common_request_message_constructer(edge_node_id, data_type_id);
    socket_sent(message, strlen(message));
    //some how gets response. 
}
