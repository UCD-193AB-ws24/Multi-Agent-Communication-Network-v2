#ifndef ECS193_API_H
#define ECS193_API_H

#include <string.h>

#define MAX_MSG_LEN 256
#define BLE_CMD_LEN 5
#define BLE_ADDR_LEN 2
#define ESCAPE_BYTE 0xFA
#define UART_START 0xFF
#define UART_END 0xFE

void uart_init();
void uart_send(String message);

#endif