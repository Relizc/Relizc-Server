import socket

from proxy import Reader, OutPacket, OutPacketGroup

class PatrolProxyListener:

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("127.0.0.1", 125))

    def listen(self):
        self.socket.listen()