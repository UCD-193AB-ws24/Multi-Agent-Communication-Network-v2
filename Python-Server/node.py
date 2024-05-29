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
        self.last_contact_time = datetime.now()
        
    def getDataLength(self, data_type):
        if data_type not in self.data_historys:
            print(f"data type {data_type} not exist")
            return (False, b'F' + "data type not exist".encode())

        # return data length
        return (True, len(self.data_historys[data_type][-1][0]))
        
    def getDataBytes(self, data_type):
        if data_type not in self.data_historys:
            print(f"data type {data_type} not exist")
            return (False, b'F' + "data type not exist".encode())

        # return latest
        return (True, self.data_historys[data_type][-1][0])
    
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