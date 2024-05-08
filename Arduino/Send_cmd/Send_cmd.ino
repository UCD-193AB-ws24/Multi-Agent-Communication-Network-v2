#include <string.h>

#define MAX_MSG_LEN 256
#define BLE_CMD_LEN 5
#define BLE_ADDR_LEN 2

void ble_send_to_root(byte* buffer, size_t length) {
  char ble_cmd[] = "SEND-";
  Serial1.print(ble_cmd);
  
  // 2 byte dst_addr, 0 for root
  byte addr[] = {0x00, 0x00}; 
  Serial1.write(addr, 2);

  // write length
  byte msg_len[1];
  msg_len[0] = (byte) length - 3; // -3 to exclude the end of message mark [E]
  Serial1.write(msg_len, 1);

  // write data
  Serial1.write(buffer, length);

  // testing
  // Serial.print(ble_cmd);
  // Serial.write(addr, 2);
  // Serial.write(msg_len, 1);
  // Serial.write(buffer, length);
  // Serial.println("");
}

void sendGPS(int p1, int p2, int p3) {
  // [D]|size_n|data_type|data_length_byte|data|...|data_type|data_length_byte|data|[E]
  byte buffer[MAX_MSG_LEN];
  byte* buf_itr = buffer;

  // message type
  strncpy((char*)buf_itr, "[D]", 3);
  buf_itr +=3;

  // 1 byte size_n of data amount, only one for GPS
  buf_itr[0] = 0x01;
  buf_itr += 1;

  // data type - 3 byte
  strncpy((char*)buf_itr, "GPS", 3);
  buf_itr +=3;

  // data len - 1 byte
  buf_itr[0] = 0x06; // 6 byte GPS data
  buf_itr += 1;

  // fake temp GPS Data - 6 byte
  buf_itr[0] = 0xff;
  buf_itr[1] = 0xff;
  buf_itr[2] = 0xff;
  buf_itr[3] = 0xff;
  buf_itr[4] = 0xff;
  buf_itr[5] = 0xff;
  buf_itr += 6;
  
  // end of message
  strncpy((char*)buf_itr, "[E]", 3);
  buf_itr +=3;

  ble_send_to_root(buffer, buf_itr - buffer);
}

void sendTestMutipleData(int16_t *fake_gps, int16_t *fake_ldc, int8_t *fake_idx) {
  // [D]|size_n|data_type|data_length_byte|data|...|data_type|data_length_byte|data|[E]
  byte buffer[MAX_MSG_LEN];
  byte* buf_itr = buffer;

  // message type
  strncpy((char*)buf_itr, "[D]", 3);
  buf_itr +=3;

  // 1 byte size_n of data amount
  buf_itr[0] = 0x03;
  buf_itr += 1;

  // ------------ data ---------------- 
  // data type - 3 byte
  strncpy((char*)buf_itr, "GPS", 3);
  buf_itr +=3;

  // data len - 1 byte
  buf_itr[0] = 0x06; // 6 byte GPS data
  buf_itr += 1;

  // fake temp GPS Data - 6 byte
  memcpy(buf_itr, fake_gps, 2);
  buf_itr += 2;
  memcpy(buf_itr, fake_gps, 2);
  buf_itr += 2;
  memcpy(buf_itr, fake_gps, 2);
  buf_itr += 2;
  
  // ------------ data ---------------- 
  // data type - 3 byte
  strncpy((char*)buf_itr, "LDC", 3);
  buf_itr +=3;

  // data len - 1 byte
  buf_itr[0] = 0x02; // 2 byte GPS data
  buf_itr += 1;

  // fake temp LDC Data - 2 byte
  memcpy(buf_itr, fake_ldc, 2);
  buf_itr += 2;

  // ------------ data ---------------- 
  // data type - 3 byte
  strncpy((char*)buf_itr, "IDX", 3);
  buf_itr +=3;

  // data len - 1 byte
  memcpy(buf_itr, fake_idx, 1);
  buf_itr += 1;

  // fake temp Data - 1 byte
  buf_itr[0] = 0xaa;
  buf_itr += 1;
  
  // end of message
  strncpy((char*)buf_itr, "[E]", 3);
  buf_itr +=3;

  ble_send_to_root(buffer, buf_itr - buffer);
}

void setup() {
  // Serial.begin(115200); // usb monitor
  // while (!Serial);
  Serial1.begin(115200); // tx-pin6 rx-pin7
  while (!Serial1);
}

int16_t fake_gps = 64000;
int16_t fake_lds = 59910;
int8_t fake_idx = 0;
void loop() {
  sendTestMutipleData(&fake_gps, &fake_lds, &fake_idx);
  fake_gps += 20;
  fake_lds += 10;
  fake_idx += 1;

  delay(5000);
}
