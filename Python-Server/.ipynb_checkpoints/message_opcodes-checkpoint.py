opcodes = {
    "Custom":      b'\x00', # will pass to app level
    "Net Info":    b'\x01',
    "Node Info":   b'\x02',
    "Root Reset":  b'\x03',
    "Data":        "D".encode(),
    "Request":     "R".encode(),
    "ECHO":        "E".encode(),
    "ACK":         "A".encode(),
    "Test":        "T".encode(),
    "Reset":       "S".encode(),
}