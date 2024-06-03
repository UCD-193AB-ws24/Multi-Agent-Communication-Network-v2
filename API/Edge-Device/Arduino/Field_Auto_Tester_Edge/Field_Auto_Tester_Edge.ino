#include <string.h>
#include <stdio.h>
#include <stdint.h>

#define MAX_MSG_LEN 256
#define BLE_CMD_LEN 5
#define BLE_ADDR_LEN 2
#define ESCAPE_BYTE 0xFA
#define UART_START 0xFF
#define UART_END 0xFE

#define MAX_TIMEOUT 100// --------------- timeout

#define REQUEST_EXAMPLE_BUTTON_PIN 5
volatile bool requestButtonPressed = false;
unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 100; // Debounce delay in milliseconds
volatile bool lastButtonState = HIGH;

uint16_t getAddr(uint8_t* bytes) {
  uint16_t hostOrderValue = (bytes[0] << 8) | bytes[1];
  return hostOrderValue;
}

// ====================== will move to other file ===========================
/* UART Base function, encode and decode uart message */
// log to Serial port that's connected with usb
void uart_log_encoded_bytes(byte* ble_cmd, size_t ble_cmd_len, byte* data_buffer, size_t data_length) {
  byte escape_byte = ESCAPE_BYTE;
  byte uart_start = UART_START;
  byte uart_end = UART_END;
  
  Serial.print("Log [");
  Serial.write(&uart_start, 1);

  // encode ble_cmd
  for (byte* byte_itr = ble_cmd; byte_itr < ble_cmd + ble_cmd_len; ++byte_itr) {
    if (byte_itr[0] < escape_byte) {
      Serial.write(byte_itr, 1);
      continue;
    }

    // need 2 byte encoded
    byte encoded = byte_itr[0] ^ escape_byte; // bitwise Xor
    Serial.write(&escape_byte, 1);
    Serial.write(&encoded, 1);
  }
  
  // encode data_buffer
  for (byte* byte_itr = data_buffer; byte_itr < data_buffer + data_length; ++byte_itr) {
    if (byte_itr[0] < escape_byte) {
      Serial.write(byte_itr, 1);
      continue;
    }

    // need 2 byte encoded
    byte encoded = byte_itr[0] ^ escape_byte; // bitwise Xor
    Serial.write(&escape_byte, 1);
    Serial.write(&encoded, 1);
  }

  Serial.write(&uart_end, 1);
  Serial.println("]");
}

// write to Serial1 port that's connected tx/rx pin
void uart_write_encoded_bytes(byte* ble_cmd, size_t ble_cmd_len, byte* data_buffer, size_t data_length) {
  byte escape_byte = ESCAPE_BYTE;
  byte uart_start = UART_START;
  byte uart_end = UART_END;
  
  Serial1.write(&uart_start, 1);

  // encode ble_cmd
  for (byte* byte_itr = ble_cmd; byte_itr < ble_cmd + ble_cmd_len; ++byte_itr) {
    if (byte_itr[0] < escape_byte) {
      Serial1.write(byte_itr, 1);
      continue;
    }

    // need 2 byte encoded
    byte encoded = byte_itr[0] ^ escape_byte; // bitwise Xor
    Serial1.write(&escape_byte, 1);
    Serial1.write(&encoded, 1);
  }
  
  // encode data_buffer
  for (byte* byte_itr = data_buffer; byte_itr < data_buffer + data_length; ++byte_itr) {
    if (byte_itr[0] < escape_byte) {
      Serial1.write(byte_itr, 1);
      continue;
    }

    // need 2 byte encoded
    byte encoded = byte_itr[0] ^ escape_byte; // bitwise Xor
    Serial1.write(&escape_byte, 1);
    Serial1.write(&encoded, 1);
  }

  Serial1.write(&uart_end, 1);
}

// Read and Decode uart message
size_t uart_readAndDecode_message(HardwareSerial& serial_port, byte* data_buffer, size_t buffer_len, size_t* data_len_ptr) {
  size_t byte_read = 0;
  size_t data_len = 0;

  if (serial_port.available() <= 0) {
    *data_len_ptr = 0;
    return 0;
  }
  
  // locate uart start
  while (serial_port.available() > 0) {
    byte data = serial_port.read();
    if (data == UART_START) {
      break;
    }
  }

  // read until uart end
  while (serial_port.available() > 0) {
    byte data = serial_port.read();
    if (data == UART_END) {
      break;
    }

    if (data == ESCAPE_BYTE) {
      byte encoded = serial_port.read();
      data = encoded ^ ESCAPE_BYTE;
      byte_read += 1;
    }

    // store this byte to data_buffer
    data_buffer[data_len] = data;
    byte_read += 1;
    data_len += 1;
  }

  if (data_len > buffer_len) {
    Serial.printf("[Error] Read %d byte decoded to %d byte > %d byte buffer length !!", byte_read, data_len, buffer_len);
  }

  *data_len_ptr = data_len;

  return byte_read;
}

size_t uart_readAndDecode_message_USB(Serial_& serial_port, byte* data_buffer, size_t buffer_len, size_t* data_len_ptr) {
  size_t byte_read = 0;
  size_t data_len = 0;

  if (serial_port.available() <= 0) {
    *data_len_ptr = 0;
    return 0;
  }
  
  // locate uart start
  while (serial_port.available() > 0) {
    byte data = serial_port.read();
    if (data == UART_START) {
      break;
    }
  }

  // read until uart end
  while (serial_port.available() > 0) {
    byte data = serial_port.read();
    if (data == UART_END) {
      break;
    }

    if (data == ESCAPE_BYTE) {
      byte encoded = serial_port.read();
      data = encoded ^ ESCAPE_BYTE;
      byte_read += 1;
    }

    // store this byte to data_buffer
    data_buffer[data_len] = data;
    byte_read += 1;
    data_len += 1;
  }

  if (data_len > buffer_len) {
    Serial.printf("[Error] Read %d byte decoded to %d byte > %d byte buffer length !!", byte_read, data_len, buffer_len);
  }

  *data_len_ptr = data_len;

  return byte_read;
}

/* Example Function, Send Data update Network Server */
void ble_send_to_root(byte* data_buffer, size_t data_length) {
  // SEND- command need 8 byte for command meta
  // SEND-|2_byte_addr|1_byte_msg_len|message
  byte ble_cmd[7] = "SEND-";
  
  // 2 byte dst_addr, 0 for root
  ble_cmd[5] = 0x00; 
  ble_cmd[6] = 0x00; 

  // write length
  // ble_cmd[7] = (byte)data_length; // no longer need length since we have uart encoder to enforce start and end of message
  uart_write_encoded_bytes(ble_cmd, 7, data_buffer, data_length);
  uart_log_encoded_bytes(ble_cmd, 7, data_buffer, data_length);
}

// ====================== will move to other file ===========================
void sendTestMultipleData(int16_t* fake_gps, int16_t* fake_ldc, int8_t* fake_idx) {
  // [D]|size_n|data_type|data_length_byte|data|...|data_type|data_length_byte|data|[E]
  byte buffer[MAX_MSG_LEN];
  byte* buf_itr = buffer;

  // message type
  strncpy((char*)buf_itr, "[D]", 3);
  buf_itr += 3;

  // 1 byte size_n of data amount
  buf_itr[0] = 0x03;
  buf_itr += 1;

  // ------------ data ---------------- 
  // data type - 3 byte
  strncpy((char*)buf_itr, "GPS", 3);
  buf_itr += 3;

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
  buf_itr += 3;

  // data len - 1 byte
  buf_itr[0] = 0x02; // 2 byte GPS data
  buf_itr += 1;

  // fake temp LDC Data - 2 byte
  memcpy(buf_itr, fake_ldc, 2);
  buf_itr += 2;

  // ------------ data ---------------- 
  // data type - 3 byte
  strncpy((char*)buf_itr, "IDX", 3);
  buf_itr += 3;

  // data len - 1 byte
  buf_itr[0] = 0x01;
  buf_itr += 1;

  // fake temp Data - 1 byte
  memcpy(buf_itr, fake_idx, 1);
  buf_itr += 1;

  // ------------ encode test \xfb data ---------------- 
  // data type - 3 byte
  strncpy((char*)buf_itr, "ESP", 3);
  buf_itr += 3;

  // data len - 1 byte
  buf_itr[0] = 0x04;
  buf_itr += 1;

  // fake temp Data - 1 byte
  buf_itr[0] = 0xfa;
  buf_itr += 1;
  buf_itr[0] = 0xfb;
  buf_itr += 1;
  buf_itr[0] = 0xfc;
  buf_itr += 1;
  buf_itr[0] = 0xfd;
  buf_itr += 1;

  ble_send_to_root(buffer, buf_itr - buffer);
}

/* Example Function, Send Request to Network Server */
void sendRobotRequest() {
  static int count = 0;
  Serial.print("Sending Robot Request: ");
  Serial.print(count++);
  Serial.print("\n");

  byte buffer[10];
  byte* buf_itr = buffer;

  // message type
  strncpy((char*)buf_itr, "REQ", 3);
  buf_itr += 3;

  // request type
  strncpy((char*)buf_itr, "Robot", 5);
  buf_itr += 5;

  ble_send_to_root(buffer, buf_itr - buffer);
}

void checkRequestButton() {
  if (requestButtonPressed) {
    // Reset the button flag
    requestButtonPressed = false;

    sendRobotRequest();
  }
}

// Interrupt Service Routine (ISR) for button press
void buttonISR() {
  unsigned long currentMillis = millis();
  bool reading = digitalRead(REQUEST_EXAMPLE_BUTTON_PIN);

  // Check if the time since the last debounce is greater than the debounce delay
  if ((currentMillis - lastDebounceTime) > debounceDelay) {
    if (reading != lastButtonState) {
      lastDebounceTime = currentMillis;
      lastButtonState = reading;

      // Check if the button state is LOW (button pressed)
      if (reading == LOW) {
        requestButtonPressed = true;
      }
    }
  }
}

void setup() {
  Serial.begin(115200); // usb monitor
  Serial1.begin(115200); // tx-pin6 rx-pin7

  pinMode(REQUEST_EXAMPLE_BUTTON_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(REQUEST_EXAMPLE_BUTTON_PIN), buttonISR, CHANGE);
  Serial.print("Finished Setup\n");
}

int16_t fake_gps = 64000;
int16_t fake_lds = 59910;
int8_t fake_idx = 0;

void network_message_handler(byte* data, size_t length) { 
  uint16_t node_addr = getAddr(data);
  char* opcode = (char*) data + 2;
  char* payload = (char*) data + 5;

  if (true) {
    byte uart_start = UART_START;
    byte uart_end = UART_END;
    Serial.print("[Handler] recived ");
    Serial.print(length);
    Serial.print(" bytes, opcode: ");
    Serial.write(opcode, 3);
    Serial.print(", payload: ");
    Serial.write((uint8_t*) payload, length - 5);
    Serial.print(", from node-");
    Serial.print(node_addr);
    Serial.print("\n");
    Serial.write(&uart_end, 1);
  }

  if (strncmp(opcode, "TST", 3) == 0) {
    // is our Test opcode 'TST'
    if (strncmp(payload, "I", 1) == 0)  {
      Serial.print("IS TST|I \n");
      byte uart_start = UART_START;
      byte uart_end = UART_END;
      // Serial.write(&uart_start, 1);
      // Serial.print("Trying to Initialize");
      // Serial.write(&uart_end, 1);
      char* test_name = payload + 1;
      // Initialization of test ...
      // Initialization of test ...
      // Initialization of test ...
      byte buffer[MAX_MSG_LEN];
      byte* buf_itr = buffer;

      // message type
      strncpy((char*)buf_itr, "CPY", 3);
      buf_itr += 3;
      memcpy(buf_itr, payload, length - 5);
      buf_itr += length - 5;
      ble_send_to_root(buffer, buf_itr - buffer);
    } else if (strncmp(payload, "S", 1) == 0)  {
      Serial.print("IS TST|S \n");
      // start test, only the reset and reconnect test example on arduino
      byte uart_start = UART_START;
      byte uart_end = UART_END;
      // Serial.write(&uart_start, 1);
      // Serial.print("Trying to Restart");
      // Serial.write(&uart_end, 1);
      byte ble_cmd[7] = "RST-E";
      
      // 2 byte dst_addr, 0 for root
      ble_cmd[5] = 0x00; 
      ble_cmd[6] = 0x00; 

      uart_write_encoded_bytes(ble_cmd, 7, ble_cmd, 0);
      uart_log_encoded_bytes(ble_cmd, 7, ble_cmd, 0);
    }
  }

}

unsigned long lastSendTime = 0;
void loop() {
  // check if there is a robot request
  unsigned long time = millis();

  checkRequestButton();

  // check if there is uart message
  byte data[1024];
  size_t data_len = 0;
  size_t byte_read = 0;
  byte_read = uart_readAndDecode_message(Serial1, data, 1024, &data_len);
  // size_t byte_read = uart_readAndDecode_message_USB(Serial, data, 1024, &data_len);

  // Debug log
  if (byte_read > 0) {
    byte uart_start = UART_START;
    byte uart_end = UART_END;
    Serial.write(&uart_start, 1);
    Serial.print("[UART] read ");
    Serial.print(byte_read);
    Serial.print(" byte \'");
    Serial.write(data, data_len);
    Serial.println("\'");
    Serial.write(&uart_end, 1);

    network_message_handler(data, data_len);
  }

  // send update
  if (time - lastSendTime >= 25000) {
    lastSendTime = time;
    sendTestMultipleData(&fake_gps, &fake_lds, &fake_idx);
    fake_gps += 20;
    fake_lds += 10;
    fake_idx += 1;
    // Serial.print(".");
  }

  delay(50);
}
