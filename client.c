#include <stdio.h>
#include <uv.h>
#include<stdlib.h>
#include<string.h>
#include <unistd.h>

#define DEFAULT_PORT 60001


void after_write(uv_write_t *req, int status){
    printf("hmm on write\n");
}

void on_connect(uv_connect_t* connection, int status) {
    if (status < 0) {
        fprintf(stderr, "Connection error: %s\n", uv_strerror(status));
        uv_close((uv_handle_t*) connection->handle, NULL);
        free(connection);
        return;
    }

    printf("Connected to server!\n");
		int end_input = 0;
    // Send data to the server
		while(end_input == 0){
			char msg[5];
    	    printf("Enter a string: ");
    	    fgets(msg, sizeof(msg), stdin);
			if(strcmp(msg, "stop") == 0){
				end_input = 1;
                return;
			}
            
			uv_buf_t buffer = uv_buf_init(msg, strlen(msg));
			uv_write_t* write_request = (uv_write_t*) malloc(sizeof(uv_write_t));
			uv_write(write_request, connection->handle, &buffer, 1, on_write);
		}
}


int main() {
    uv_loop_t* loop = uv_default_loop();

    // Initialize TCP handle
    uv_tcp_t* client = (uv_tcp_t*) malloc(sizeof(uv_tcp_t));
    uv_tcp_init(loop, client);

    // Set up server address and port
    struct sockaddr_in server_addr;
    uv_ip4_addr("127.0.0.1", DEFAULT_PORT, &server_addr);

    // Create connection request
    uv_connect_t* connect_request = (uv_connect_t*) malloc(sizeof(uv_connect_t));
    uv_tcp_connect(connect_request, client, (const struct sockaddr*) &server_addr, on_connect);

    // Start the event loop
    uv_run(loop, UV_RUN_DEFAULT);

    // Cleanup
    uv_loop_close(loop);
    free(client);
    free(connect_request);
    // thread stop here
    printf("exit\n");

    return 0;
}