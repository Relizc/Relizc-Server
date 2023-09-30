import socket
import logger

from proxy import Status, Reader, OutPacket, OutPacketGroup

class MatchmakingProxy:

    def __init__(self):

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("127.0.0.1", 127))
        self.socket.listen()
        self.LOG = logger.Logger(self)
