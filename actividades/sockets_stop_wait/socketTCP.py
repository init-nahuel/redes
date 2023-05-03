import socket
import random

class socketTCP:
    def __init__(self) -> None:
        self.dest_address = None
        self.udp_socket = socket.socket()
        self.orig_address = None
        self.seq = None # random.randint(0, 100)
    