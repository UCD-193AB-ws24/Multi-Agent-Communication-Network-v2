import serial
import threading
import time
from datetime import datetime

ESCAPE_BYTE_BS = b'\xfa'  # byte string of 0xfa
ESCAPE_BYTE = ESCAPE_BYTE_BS[0]  # int type == 0xfa == 250
UART_START = b'\xff'
UART_END = b'\xfe'

class UartManager:
    def __init__(self, serial_port, uart_baud_rate):
        self.serial_port = serial_port
        self.uart_baud_rate = uart_baud_rate
        self.serial_connection = None
        self.uart_thread = None
        self.callback_func = None
        self.is_serial_connected = False
    
    def run(self):
        self.uart_thread = threading.Thread(
            target=self.uart_listening_thread, daemon=True
        )
        self.uart_thread.start()
    
    def attach_callback(self, callback_func):
        self.callback_func = callback_func
            
    def uart_connect(self, serial_port, uart_baud_rate):
        if serial_port:
            self.serial_port = serial_port
        if uart_baud_rate:
            self.uart_baud_rate = uart_baud_rate

        if self.serial_connection and (serial_port and self.serial_port != serial_port):
            self.serial_connection.close()
            self.serial_connection = None
            self.is_serial_connected = False

        if self.serial_connection:
            print("UART port already connected:", self.serial_port)
            self.is_serial_connected = True
            return

        try:
            self.serial_connection = serial.Serial(self.serial_port, self.uart_baud_rate)
            self.is_serial_connected = True
            print(f"{datetime.now()} - Connected to serial port {self.serial_port}")
        except Exception as e:
            print(f"{datetime.now()} - Unable to connect to serial port {self.serial_port}: {e}")
    
    def uart_listening_thread(self):
        print(f"{datetime.now()} - Starting UART listening thread")

        while True:
            if self.serial_connection is not None:
                self.is_serial_connected = True
                print(f"{datetime.now()} - Listening for UART messages")
                try:
                    uart_message = self.uart_read_message()
                    print(f"{datetime.now()} - Received UART message: {uart_message}")
                    self.uart_handler(uart_message)
                    continue  # Successfully read one message
                except serial.SerialException as e:
                    print(f"{datetime.now()} - Serial communication error: {e}")
                    self.serial_connection = None  # Reset the connection
                except Exception as e:
                    print(f"{datetime.now()} - Unexpected error: {e}")
            else:
                self.uart_connect(self.serial_port, self.uart_baud_rate)
                time.sleep(3)
    
    def uart_handler(self, data):
        print(f"{datetime.now()} - Received UART data:")
        if self.callback_func:
            self.callback_func(data)
    
    def uart_read_message(self):
        data = b''
        while True:
            if self.serial_connection.in_waiting > 0:  # Check if there is data available to read
                byte = self.serial_connection.read() # Read and decode the data
                # print(byte, end="-")
                if byte == UART_START:
                    # start of message
                    data = b''
                    continue
                if byte == UART_END:
                    # found end of message sequence
                    break

                data += byte
        
        # decode the raw uart signals
        return self.uart_decoder(data)
    
    def send_data(self, data):
        if self.serial_connection != None:
            data_encoded = self.uart_encoder(data)
            self.serial_connection.write(UART_START) # spcial byte marking start
            self.serial_connection.write(data_encoded)
            self.serial_connection.write(UART_END)   # spcial byte marking end
            print(f"{datetime.now()} - Sent data: {data}")
            return b'S'
        else:
            return b'F' + "No Serial Connection".encode()

    def uart_decoder(self, data):
        result = b''
        
        print(f"{datetime.now()} - Decoding data: {data}")
        i = 0
        while i < len(data):
            byte = data[i] # python gets the int type of single byte
            
            if byte != ESCAPE_BYTE:
                result += byte.to_bytes(1, 'big') # get the bytestring of this byte
                i += 1 # processed 1 byte for normal byte
                continue
            
            # byte == escape_byte, decode escaped byte
            byte_encoded = data[i + 1]
            byte_decoded = byte_encoded ^ 0xff
            result += byte_decoded.to_bytes(1, 'big') # get the bytestring of this byte
            i += 2 # processed 2 byte for encoded byte

        print(f"{datetime.now()} - Decoded data: {result}")
        return result
    
    def uart_encoder(self, data):
        print(f"{datetime.now()} - Encoding data: {data}")
        result = b''
        
        for byte in data:
            if byte >= ESCAPE_BYTE:
                result += ESCAPE_BYTE.to_bytes(1, 'big') + (byte ^ 0xff).to_bytes(1, 'big')
            else:
                result += byte.to_bytes(1, 'big')
            
        print(f"{datetime.now()} - Encoded data: {result}")
        return result