socket_event_subscriber = {}

def subscribe(opcode, callback):
    if opcode not in socket_event_subscriber:
        socket_event_subscriber[opcode] = []
        
    socket_event_subscriber[opcode].append(callback)
    
def unsubscribe(opcode, callback):
    if opcode not in socket_event_subscriber:
        print(f"opcode: \'{opcde}\' has no subscriber")
        return
    
    if callback not in socket_event_subscriber[opcode]:
        print(f"opcode: \'{opcde}\' has no subscriber from this callback")
        return
    
    socket_event_subscriber[opcode].remove(callback)
    
def notify(opcode, data):
    if opcode in socket_event_subscriber:
        for callback in socket_event_subscriber[opcode]:
            try:
                callback(data)
            except Exception as e:
                print(f"Error occurred when invoke callback for \'{opcode}\'")
                print(f"Error: {e}")
                unsubscribe(opcode, callback)