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

    # ========== Data Management ==========

    def getDataLength(self, data_type):
        if data_type not in self.data_historys:
            print(f"data type {data_type} not exist")
            return (False, b'F' + "data type not exist".encode())
        return (True, len(self.data_historys[data_type][-1][0]))

    def getDataBytes(self, data_type):
        if data_type not in self.data_historys:
            print(f"data type {data_type} not exist")
            return (False, b'F' + "data type not exist".encode())
        return (True, self.data_historys[data_type][-1][0])

    def storeData(self, data_type, data):
        if data_type not in self.data_historys:
            self.data_historys[data_type] = deque()

        time = datetime.now()
        self.data_historys[data_type].append((data, time))
        log_data_hist(data_type, data, time)

        if len(self.data_historys[data_type]) > 10:
            self.data_historys[data_type].popleft()

    # ========== Status Management ==========

    def update_status(self, status):
        self.status = status