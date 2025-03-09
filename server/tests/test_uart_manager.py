import unittest
from uart_manager import UartManager, escape_byte

class TestUartManager(unittest.TestCase):
    def setUp(self):
        self.uart_manager = UartManager('/dev/ttyUSB0', 115200)  # Use a dummy port for testing

    def test_uart_encoder(self):
        print("Test encoding of data")
        data = b'SEND-\x00\x00![D]\x03GPS\x06\x04\x05\x04\x05\x04\x05LDC\x02\x88\xefIDX\x01\x8dESP\x04\xfa\xfb\xfc\xfd'
        expected_encoded_data = b'SEND-\x00\x00![D]\x03GPS\x06\x04\x05\x04\x05\x04\x05LDC\x02\x88\xefIDX\x01\x8dESP\x04\xfa\x05\xfa\x04\xfa\x03\xfa\x02'
        
        encoded_data = self.uart_manager.uart_encoder(data)
        self.assertEqual(encoded_data, expected_encoded_data)

    def test_uart_decoder(self):
        print("Test decoding of data")
        encoded_data = b'SEND-\x00\x00![D]\x03GPS\x06\x04\x05\x04\x05\x04\x05LDC\x02\x88\xefIDX\x01\x8dESP\x04\xfa\x05\xfa\x04\xfa\x03\xfa\x02'
        expected_decoded_data = b'SEND-\x00\x00![D]\x03GPS\x06\x04\x05\x04\x05\x04\x05LDC\x02\x88\xefIDX\x01\x8dESP\x04\xfa\xfb\xfc\xfd'
        
        decoded_data = self.uart_manager.uart_decoder(encoded_data)
        self.assertEqual(decoded_data, expected_decoded_data)

if __name__ == '__main__':
    unittest.main()