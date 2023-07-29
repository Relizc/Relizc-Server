import socket

from proxy import Reader, OutPacket, OutPacketGroup

class ProxyPatrol:

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("127.0.0.1", 125))
        self.socket.listen()

        while True:
            con, addr = self.socket.accept()
            data = con.recv(1024)
            #print(f"data: {data}, addr: {addr}")

            packet = Reader(data)
            typ = packet.readByte()

            if typ == 0xd0:
                # add player
                print(packet)
