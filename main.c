#include "socket.h"

void cb (char* msg){
    test_sent(msg);
}

int main(){
    // test_sent("My brain blew up");
    pthread_t tid;
    void (*callback) (char*) = cb;
    tid = init_socket(cb);
    printf("back to main\n");
    test_sent("============================================");
    test_sent("----------------------------------------------");
    if (pthread_join(tid, NULL) != 0) {
        perror("pthread_join");
        return 1;
    }
    printf("after join\n");
    
}
