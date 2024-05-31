import serial
import threading
import time

# ==== protocal constents ==== Need to be defined in seperate file
escape_byte_bs = b'\xfa' # byte string of 0xfa
escape_byte = escape_byte_bs[0] # int type == 0xfa == 250
uart_start = b'\xff'
uart_end = b'\xfe'

class Uart_Manager:
    def __init__(self, uart_port, uart_baud_rate):
        self.uart_port = uart_port
        self.uart_baud_rate = uart_baud_rate
        self.serial_connection = None
        self.uart_thread = None
        self.callback_func = None
        
        self.uart_connect()
            
    def uart_connect(self, uart_port, uart_baud_rate):
        # close current port
        if self.uart_port != uart_port and self.serial_connection != None:
            self.serial_connection.close()
            self.serial_connection = None
        
        self.uart_port = uart_port
        self.uart_baud_rate = uart_baud_rate
        self.connect()
            
    def uart_connect(self):
        if self.serial_connection != None:
            print("Uart port already connected:", self.uart_port)
            return
        
        # try connect to new port
        try:
            self.serial_connection = serial.Serial(self.uart_port, self.uart_baud_rate)
            print("connected to serial port", self.uart_port)
        except:
            print("unable to connect to serial port", self.uart_port)
        
        
    def uart_event_handler(self, data):
        # print("recived uart data:")
        self.callback_func(data)
    
    # for uart protocal,  -------------------- TB Tested --------------------------
    def uart_decoder(self, data):
        # decode escape bytes
        result = b''
        
        i = 0
        while i < len(data):
            byte = data[i] # python gets the int type of single byte
            
            if byte != escape_byte:
                result += byte.to_bytes(1, 'big') # get the bytestring of this byte
                i += 1 # processed 1 byte for normal byte
                continue
            
            # byte == escape_byte, decode escaped byte
            byte_encoded = data[i + 1]
            byte_decoded = escape_byte ^ byte_encoded
            result += byte_decoded.to_bytes(1, 'big') # get the bytestring of this byte
            i += 2 # processed 2 byte for encoded byte
        # while loop done
        
        # print("[Encoded]", data)
        # print("[Decoded]", result)
        return result
    
    # for uart protocal, -------------------- TB Tested --------------------------
    def uart_encoder(self, data):
        # encode escape bytes
        result = b''
        for byte in data:
            if byte < escape_byte:
                result += byte.to_bytes(1, 'big') # get the bytestring of this byte
                continue
            
            # byte >= escape_byte, encode escaped byte
            byte_encoded = escape_byte ^ byte
            result += escape_byte.to_bytes(1, 'big') # get the bytestring of this byte
            result += byte_encoded.to_bytes(1, 'big') # get the bytestring of this byte
        # while loop done
        
        return result
    
    def sent_data(self, data):
        if self.serial_connection != None:
            data_encoded = self.uart_encoder(data)
            self.serial_connection.write(uart_start) # spcial byte marking start
            self.serial_connection.write(data_encoded)
            self.serial_connection.write(uart_end)   # spcial byte marking end
            return b'S'
        else:
            return b'F' + "No Serial Connection".encode()
    
    def attack_callback(self, callback_func):
        self.callback_func = callback_func
        print(f"[Uart] Successfully attached callback function, {type(self.callback_func)}")
    
    # read the entire message base on protocal, -------------------- TB Finish --------------------------
    def uart_read_message(self):
        # read the entire message base on our uart escape byte protocal
        # TB Test
        data = b''
        while True:
            if self.serial_connection.in_waiting > 0:  # Check if there is data available to read
                byte = self.serial_connection.read() # Read and decode the data
                # print(byte, end="-")
                if byte == uart_start:
                    # start of message
                    data = b''
                    continue
                if byte == uart_end:
                    # found end of message sequence
                    break

                data += byte
        # end of while loop
        
        # decode the raw uart signals
        return self.uart_decoder(data)
    
    def uart_listening_thread(self):
        print("=== Enter uart listening thread === ")
        # listen to urat port
        # self.sent_data("[LOGOF]--".encode())
        
        while True:
            if self.serial_connection != None:
                try:
                    uart_message = self.uart_read_message()
                    self.uart_event_handler(uart_message)
                    # print("> returend from uart handler")  # [Testing Log]
                    continue # successfuly read one message
                except serial.SerialException as e:
                    print(f"Serial communication error: {e}")
                    self.serial_connection = None # reset the connection
                except:
                    pass
            else:
                # No connection
                print("Uart trying to reconnect...")
                self.uart_connect()
                time.sleep(3)
    
    def run(self):
        print("Starting uart thread")
        self.uart_thread = threading.Thread(target=self.uart_listening_thread, args=(), daemon=True)
        self.uart_thread.start()
        print("Started uart thread")