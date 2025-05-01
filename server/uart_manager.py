import serial
import threading
import time
import re

ESCAPE_BYTE = 0xFA
UART_START = b'\xFF'
UART_END = b'\xFE'

class UartManager:
    def __init__(self, serial_port, uart_baud_rate):
        self.serial_port = serial_port
        self.uart_baud_rate = uart_baud_rate
        self.serial_connection = None
        self.uart_thread = None
        self.callback_func = None
        self.is_serial_connected = False

    def log(self, level, message):
        print(f"[UART][{level}]  - {message}")

    def run(self):
        self.uart_thread = threading.Thread(target=self.uart_listening_thread, daemon=True)
        self.uart_thread.start()

    def attach_callback(self, callback_func):
        self.callback_func = callback_func

    def uart_connect(self, serial_port=None, uart_baud_rate=None):
        if serial_port: self.serial_port = serial_port
        if uart_baud_rate: self.uart_baud_rate = uart_baud_rate
        if self.serial_connection:
            self.serial_connection.close()
        try:
            self.serial_connection = serial.Serial(self.serial_port, self.uart_baud_rate)
            self.is_serial_connected = True
            self.log("INFO", f"Connected to {self.serial_port}")
        except Exception as e:
            self.log("ERROR", f"Connection failed: {e}")

    def uart_listening_thread(self):
        self.log("INFO", "Starting UART listening thread")
        while True:
            if self.serial_connection:
                self.log("INFO", "Listening for UART messages")
                try:
                    data = self.uart_read_message()
                    self.log("RECEIVE", f"Raw UART message: {data}")
                    self.uart_handler(data)
                except Exception as e:
                    self.log("ERROR", f"UART error: {e}")
                    self.serial_connection = None
            else:
                self.uart_connect()
                time.sleep(3)

    def uart_handler(self, data):
        self.log("RECEIVE", "Processing UART data")
        if self.callback_func:
            cleaned = self.clean_uart_message(data)
            self.log("CLEAN", f"Cleaned UART message: {cleaned}")
            self.callback_func(cleaned)

    def uart_read_message(self):
        data = b''
        while True:
            if self.serial_connection.in_waiting:
                byte = self.serial_connection.read()
                if byte == UART_START:
                    data = b''
                elif byte == UART_END:
                    break
                else:
                    data += byte
        return self.uart_decoder(data)

    def send_data(self, data):
        if self.serial_connection:
            encoded = self.uart_encoder(data)
            self.serial_connection.write(UART_START)
            self.serial_connection.write(encoded)
            self.serial_connection.write(UART_END)
            self.log("SEND", f"Sent data: {data}")
            return b'S'
        else:
            return b'F' + b"No Serial Connection"

    def uart_decoder(self, data):
        self.log("DECODE", f"Raw: {data}")
        result = b''
        i = 0
        while i < len(data):
            byte = data[i]
            if byte != ESCAPE_BYTE:
                result += bytes([byte])
                i += 1
            else:
                result += bytes([data[i+1] ^ 0xFF])
                i += 2
        self.log("DECODE", f"Decoded: {result}")
        return result

    def uart_encoder(self, data):
        self.log("SEND", f"Encoding data: {data}")
        result = b''
        for byte in data:
            if byte >= ESCAPE_BYTE:
                result += bytes([ESCAPE_BYTE]) + bytes([byte ^ 0xFF])
            else:
                result += bytes([byte])
        self.log("SEND", f"Encoded: {result}")
        return result

    def clean_uart_message(self, data: bytes) -> bytes:
        ansi_escape = re.compile(rb'\x1b\[[0-9;]*m')
        data = ansi_escape.sub(b'', data)
        filtered = []
        for line in data.split(b'\n'):
            if b'I (' in line or b'W (' in line or b'E (' in line:
                continue
            filtered.append(line.strip())
        return b'\n'.join(filtered)
