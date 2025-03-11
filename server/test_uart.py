import time
from uart_manager import UartManager

# Define the serial port and baud rate
SERIAL_PORT = '/dev/tty.usbserial-1430'  # Replace with the actual serial port
BAUD_RATE = 115200

# Initialize the UartManager
uart_manager = UartManager(SERIAL_PORT, BAUD_RATE)

# Attach a callback function to handle received data
def uart_callback(data):
    print(f"Received data: {data}")

uart_manager.attach_callback(uart_callback)

# Connect to the UART port
uart_manager.uart_connect(SERIAL_PORT, BAUD_RATE)

# Run the UART listening thread
uart_manager.run()

# Wait for the connection to be established
time.sleep(2)

# Send the NINFO command to get network information
command = "NINFO"
uart_manager.send_data(command.encode())

# Wait for a response
time.sleep(5)