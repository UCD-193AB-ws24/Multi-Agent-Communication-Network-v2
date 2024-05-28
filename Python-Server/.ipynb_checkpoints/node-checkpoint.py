from enum import Enum
from collections import deque
from datetime import datetime
import os

# Structure of Node
# No need for big change at the moment, will get final review and clean up when other stuff is confirmed working
# - need to remvoe the restriction of only servering GPS (not now)

def log_data_hist(data_type, data, time):
    file_path = log_folder + "/" + data_type + "_hist.txt"
    try:
        with open(file_path, 'a') as log_file:
            # Write text followed by a newline to the log file
            log_file.write(str(data) + ", " + str(time) + '\n')
    except:
        print("Can't log data to log_file", data_type, data)

class Node_Status(Enum):
    Active = 1
    Idol = 2
    Disconnect = 3
    
class Node:
    def __init__(self, name:str, address: int, uuid: bytes):
        self.name = name
        self.address = address
        self.uuid = uuid
        
        self.status = Node_Status.Active
        self.data_historys = {}
        
        self.data_historys["GPS"] = deque()            # (gps_data, time)
        self.data_historys["Load_Cell"] = deque()      # (load_data, time)
        self.data_historys["Robot_Request"] = deque()  # (request_count, time)
        self.last_contact_time = datetime.now()
        
#     def getData(self, data_type):
#         # ====== might not need this function anymore =========
#         # ====== since only cares about data's bytes=========
#         if data_type not in self.data_historys:
#             print(f"data type {data_type} not exist")
#             return None
        
#         return self.data_historys[data_type][-1][0]
        
    def getDataBytes(self, data_type):
        # ====== for GPS only for now =========
        # TB Finish - complte other data type
        # GPS - 6 byte - lontitude|latitude
        # ====== for GPS only for now =========
        
        # if data_type == "GPS":
            # gps_data = self.data_historys[data_type][-1][0]
            # data_byte = b''
            # data_byte += gps_data[0].to_bytes(3, byteorder='little')
            # data_byte += gps_data[1].to_bytes(3, byteorder='little')
            
            # return data_byte
        
        if data_type not in self.data_historys:
            print(f"data type {data_type} not exist")
            return b'F'

        return self.data_historys[data_type][-1][0]
    
    def storeData(self, data_type, data):
        if data_type not in self.data_historys:
            self.data_historys[data_type] = deque()
        
        time = datetime.now()
        self.data_historys[data_type].append((data, time))
        log_data_hist(data_type, data, time)
        
        # only kept latest 10 data in server
        if len(self.data_historys[data_type]) > 10:
            self.data_historys[data_type].popleft()
            
    def update_status(self, status):
        # need to implment how in detile the status affects Node's other function
        # TB Finish
        self.status = status