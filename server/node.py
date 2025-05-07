from enum import Enum
from collections import deque
from datetime import datetime

# ========== Node Status Enum ==========

class Node_Status(Enum):
    Active = 1
    Idle = 2
    Disconnect = 3

# ========== Node Class ==========

class Node:
    def __init__(self, name: str, address: int, uuid: bytes):
        self.name = name
        self.address = address
        self.uuid = uuid
        self.status = Node_Status.Active
        self.data_historys = {}
        self.last_contact_time = datetime.now()
        self.missed_updates = 0
        self.gps = None  # Tuple of (lon, lat) as integers

    # ========== Data Management ==========

    def getDataLength(self, data_type):
        if data_type == "GPS" and self.gps is not None:
            return (True, 6)  # 3 bytes for lon, 3 bytes for lat

        if data_type not in self.data_historys:
            print(f"data type {data_type} not exist")
            return (False, b'F' + "data type not exist".encode())
        return (True, len(self.data_historys[data_type][-1][0]))

    def getDataBytes(self, data_type):
        if data_type == "GPS":
            if self.gps is None:
                print("GPS data not set")
                return (False, b'F' + "GPS data not set".encode())
            lon, lat = self.gps
            data_bytes = b''
            data_bytes += int(lon).to_bytes(3, byteorder='little', signed=True)
            data_bytes += int(lat).to_bytes(3, byteorder='little', signed=True)
            return (True, data_bytes)

        if data_type not in self.data_historys:
            print(f"data type {data_type} not exist")
            return (False, b'F' + "data type not exist".encode())
        return (True, self.data_historys[data_type][-1][0])

    def storeData(self, data_type, data):
        if data_type == "GPS":
            self.set_gps_from_bytes(data)
            return

        if data_type not in self.data_historys:
            self.data_historys[data_type] = deque()

        time = datetime.now()
        self.data_historys[data_type].append((data, time))
        log_data_hist(data_type, data, time)

        if len(self.data_historys[data_type]) > 10:
            self.data_historys[data_type].popleft()

    def set_gps(self, lat, lon):
        # Accepts floats or ints and converts to fixed-point integers
        try:
            lat_int = int(float(lat) * 1000)
            lon_int = int(float(lon) * 1000)
            self.gps = (lon_int, lat_int)
        except ValueError:
            print("Invalid GPS values provided.")
    
    def update_gps(self, lat: float, lon: float):
        self.gps = (lat, lon)

    def set_gps_from_bytes(self, data_bytes):
        if len(data_bytes) != 6:
            print("Invalid GPS data length")
            return
        lon = int.from_bytes(data_bytes[0:3], byteorder='little', signed=True)
        lat = int.from_bytes(data_bytes[3:6], byteorder='little', signed=True)
        self.gps = (lon, lat)

    # ========== Status Management ==========

    def update_status(self, status):
        self.status = status