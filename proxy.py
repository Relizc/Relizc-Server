
import socket
import tkinter as tk
import tkinter.messagebox as tkmsg

import logger
import rsglobal
import datetime
import time
import json
import os
import threading
import traceback
import random

class Status:

    NULL = b"\x00"
    OK = b"\x01"
    JSON = b"\x02"
    NO_PERM = b"\x11"
    NO_AUTH = b"\x10"
    INTERNAL_ERR = b"\xa0"

class Reader:

    def __init__(self, data=b""):
        self.data = data
        self.pointer = 0

    def readServerCode(self):
        b = self.readByte()
        if b == 0x00:
            return "T"
        elif b == 0x01:
            return "S"
        elif b == 0x02:
            return "M"
        elif b == 0x03:
            return "B"
        elif b == 0x04:
            return "G"

    def readByte(self):
        x = self.data[self.pointer]
        self.pointer += 1
        if isinstance(x, int):
            return x
        return ord(x)
                         
    def readShort(self):
        n = 0
        for i in range(2):
            n += self.readByte() * 256 ** i
        return n
    

    def readSignedShort(self):
        return self.readShort() - 32768

    def readInteger(self):
        n = 0
        for i in range(4):
            n += self.readByte() * 256 ** i
        return n

    def readLong(self):
        n = 0
        for i in range(8):
            n += self.readByte() * 256 ** i
        return n

    def readSignedLong(self):
        return self.readLong() - 9223372036854775808

    def readSignedInteger(self):
        return self.readInteger() - 2147483648

    def readString(self):
        size = self.readShort()
        x = ""
        for i in range(size):
            x += chr(self.readByte())
        return x

    def readBoolean(self):
        if self.readByte():
            return True
        return False

    def readTypeArray(self):
        typ_i = self.readByte()
        typ = self.types[typ_i]
        size = self.readShort()
        arr = []
        for i in range(size):
            arr.append(typ(self))
        return arr

    def readMixedArray(self):
        size = self.readShort()
        arr = []
        for i in range(size):
            typ_i = self.readByte()
            typ = self.types[typ_i]
            arr.append(typ(self))
        return arr

    def writeByte(self, b):
        self.data += bytes(chr(b).encode("latin-1"))

    def writeShort(self, s):
        if s > 65535:
            raise TypeError("s must < 65536!")
        if s < 0:
            raise TypeError("s must >= 0! Otherwise use writeSignedShort")
        for i in range(2):
            b = int(s % 256)
            self.writeByte(b)
            s = (s - b) / 256

    def writeSignedShort(self, s):
        if s > 32767:
            raise TypeError("s must < 32767! Otherwise use writeShort!")
        if s < -32768:
            raise TypeError("s must >= -32768!")
        s += 32768
        self.writeShort(s)

    def writeString(self, s):
        if len(s) > 65535:
            raise TypeError("String is too long! Max len is 65535!")
        self.writeShort(len(s))
        for i in s:
            self.writeByte(ord(i))

    def writePureBytes(self, b):
        self.data += b

    types = {
        0: readByte,
        1: readShort,
        2: readSignedShort,
        3: readInteger,
        4: readSignedInteger,
        5: readString,
        6: readTypeArray,
        7: readMixedArray,
        8: readBoolean
    }

class OutPacket:

    def __init__(self, typebyte):
        self.data = b""
        self.writeByte(typebyte)

    def writeByte(self, b):
        self.data += bytes(chr(b).encode("latin-1"))

    def writeShort(self, s):
        if s > 65535:
            raise TypeError("s must < 65536!")
        if s < 0:
            raise TypeError("s must >= 0! Otherwise use writeSignedShort")
        for i in range(2):
            b = int(s % 256)
            self.writeByte(b)
            s = (s - b) / 256

    def writeInteger(self, i):
        if s > 2147483647:
            raise TypeError("s must < 2147483647!")
        if s < 0:
            raise TypeError("s must >= 0! Otherwise use writeSignedInteger")
        for i in range(4):
            b = int(s % 256)
            self.writeByte(b)
            s = (s - b) / 256

    def writeSignedShort(self, s):
        if s > 32767:
            raise TypeError("s must < 32767! Otherwise use writeShort!")
        if s < -32768:
            raise TypeError("s must >= -32768!")
        s += 32768
        self.writeShort(s)

    def writeString(self, s):
        if len(s) > 65535:
            raise TypeError("String is too long! Max len is 65535!")
        self.writeShort(len(s))
        for i in s:
            self.writeByte(ord(i))

    def writeTypeArray(self, a):
        if len(a) == None:
            self.writeByte(0)
            self.writeShort(0)
            return
        first = True
        for i in a:
            if first:
                self.writeByteType(i)
                self.writeShort(len(a))
                first = False
            self.writeByObjectClass(i)

    def writeMixedArray(self, a):
        self.writeShort(len(a))
        if len(a) == 0:
            return
        for i in a:
            self.writeByteType(i)
            self.writeByObjectClass(i)
                

    def writeByteType(self, obj):
        if isinstance(obj, bytes):
            self.writeByte(0x00)
        elif isinstance(obj, int):
            if obj < 65536:
                self.writeByte(0x01)
            elif obj < 2147483648:
                self.writeByte(0x03)
        elif isinstance(obj, list):
            self.writeByte(0x07)
        elif isinstance(obj, str):
            self.writeByte(0x05)

    def writeByObjectClass(self, obj):
        if isinstance(obj, bytes):
            self.writeByte(obj)
        elif isinstance(obj, int):
            if obj < 65536:
                self.writeShort(obj)
            elif obj < 2147483648:
                self.writeInt(obj)
        elif isinstance(obj, list):
            self.writeMixedArray(obj)
        elif isinstance(obj, str):
            self.writeString(obj)


class OutPacketGroup:

    def __init__(self, group):
        self.group = group
        self.data = Reader()
        self.data.writeShort(len(group))
        for i in self.group:
            self.data.writeShort(len(i.data))
            self.data.writePureBytes(i.data)
        
        

class ProxyListener:

    def __init__(self, servers, server_list, opened_details, bungee, argv, players, inf):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("127.0.0.1", 127))
        self.socket.listen()
        self.servers = servers
        self.server_list = server_list
        self.player_list = players
        self.bungee = bungee
        self.opened_details = opened_details
        self.LOG = logger.Logger(self)
        self.awaitWarps = []
        self.argv = argv
        self.subawaitwarp = []
        self.cansubwarp = []
        self.info = inf



        while True:
            #print('waiting for connection...')

            con, addr = self.socket.accept()
            data = con.recv(1024)
            #print(f"data: {data}, addr: {addr}")

            packet = Reader(data)
            typ = packet.readByte()

            self.info["rx"] += 1

            try:
                if typ == 1:
                    ram = packet.readByte()
                    temp = packet.readString()
                    idd = packet.readString()
                    name = packet.readString()
                    svtype = packet.readString()
                    port = packet.readShort()
                    for i in self.server_list:
                        if i.id == idd:
                            i.status = rsglobal.SERVER_STATUS.RUNNING

                            for j in self.subawaitwarp:
                                if j[1] == (rsglobal.SERVER_RAM_BYTENUM[ram] + idd):
                                    
                                    crt = OutPacket(0xe9)
                                    crt.writeString(j[1])
                                    crt.writeString(j[0])
                                    self.bungee.queued.append(crt)

                                    self.LOG.info("Newly created " + (rsglobal.SERVER_RAM_BYTENUM[ram] + idd) + "! Sending " + j[0] + " to it!")




                            break
                    else:
                        srv = rsglobal.DynamicServer(temp, rsglobal.SERVER_RAM_BYTENUM[ram], sid = idd, name = name, type = svtype, handleFile = False)
                        srv.att = "Unverified: Server is created via unexsistent."
                        self.server_list.append(srv)

                    con.send(OutPacketGroup([]).data.data)
                    con.close()

                    crt = OutPacket(0xe2)
                    crt.writeByte(ram)
                    crt.writeString(idd)
                    crt.writeShort(port)

                    if svtype == "verify":
                        c = 0x00
                        d = 0
                    elif svtype.startswith("lobby"):
                        c = 0x01
                        if svtype == "lobby-main":
                            d = 0
                        if svtype == "lobby-bridge":
                            d = 31
                        if svtype == "lobby-deathswap":
                            d = 42
                        if svtype == "lobby-smp":
                            d = 1
                    elif svtype.startswith("smp"):
                        c = 0x02
                        d = 0
                    else:
                        c = 0x7f
                        d = 0
                    crt.writeByte(c)
                    crt.writeShort(d)
                    self.bungee.queued.append(crt)

                    
                    continue


                
                if typ == 0xa2:
                    ram = packet.readByte()
                    idd = packet.readString()
                    msg = packet.readString()

                    print(f"KEYset diagnostic alert {ram} {idd} {msg}")

                    threading.Thread(target=lambda: tkmsg.showerror(f"[RS-{rsglobal.SERVER_RAM_BYTENUM[ram] + idd}] Broadcast System", datetime.datetime.now().strftime("%H:%M:%S") + f" An internal error occured on server [RS-{rsglobal.SERVER_RAM_BYTENUM[ram] + idd}]:\n\n" + msg)).start()
                    con.send(Status.OK)
                    con.close()
                    continue
                if typ == 0xa0:
                    ram = packet.readByte()
                    idd = packet.readString()
                    t = packet.readByte()
                    msg = packet.readString()

                    print(f"KEYset diagnostic custom {ram} {idd} {t} {msg}")

                    m = datetime.datetime.now().strftime("%H:%M:%S") + " " + msg
                    if t == 0:
                        func = tkmsg.showinfo
                    elif t == 1:
                        func = tkmsg.showwarning
                    elif t == 2:
                        func = tkmsg.showerror
                    threading.Thread(target=lambda: func(f"[RS-{rsglobal.SERVER_RAM_BYTENUM[ram] + idd}] Alert", m)).start()
                    con.send(OutPacketGroup([]).data.data)
                    con.close()
                    continue

                if typ == 0x51:
                    field = packet.readByte()
                    ram = packet.readServerCode()
                    idd = packet.readString()

                    server = ram + idd
                    for i in self.server_list:
                        if i.fullId.lower() == server.lower():
                            server = i
                            break
                    else:
                        con.send(OutPacketGroup([]).data.data)
                        con.close()
                        continue



                    con.send(OutPacketGroup([]).data.data)
                    con.close()

                    if field == 0x01:
                        server.att = packet.readString()

                    continue

                if typ == 0xe8:
                    t = ""
                    ram = packet.readServerCode()
                    idd = packet.readString()
                    nom = packet.readByte()

                    print(ram, idd, nom)

                    if nom == 0x00:

                        c = packet.readServerCode()
                        d = packet.readString()

                        e = packet.readString()

                        print(c, d, e)

                        crt = OutPacket(0xe9)
                        crt.writeString(c + d)
                        crt.writeString(e)
                        self.bungee.queued.append(crt)

                        con.send(OutPacketGroup([]).data.data)
                        con.close()
                        continue
                    elif nom == 0x01:

                        cat = packet.readByte()
                        sub = packet.readShort()
                        nam = packet.readString()

                        print(cat, sub, nam)

                        shuffle = False

                        if cat == 0x00:
                            t = "verify"
                            shuffle = True
                        elif cat == 0x01:
                            if sub == 0:
                                t = "lobby-main"
                                shuffle = True
                            elif sub == 31:
                                t = "lobby-bridge"
                                shuffle = True
                            elif sub == 42:
                                t = "lobby-deathswap"
                                shuffle = True
                            elif sub == 1:
                                t = "lobby-smp"
                                shuffle = True
                        elif cat == 0x02:
                            t = "smp"
                            shuffle = False
                        elif cat == 0x03:
                            if sub == 13:
                                t = "game-bridge"
                                shuffle = True
                        elif cat == 0x04:
                            if sub==1:
                                t="build-public"
                                shuffle=False

                        got = None

                        n = []

                        for i in self.server_list:
                            if i.type == t:
                                for x in i.players:
                                    if x[0].lower() == nam.lower():
                                        break
                                else:
                                    if len(i.players) < i.maxplayers:
                                        n.append(i)
                                        break

                        o = OutPacket(0xe8)
                        o.writeShort(len(n))
                        o.writeString(nam)

                        if len(n) != 0:
                            got = n[random.randint(0, len(n) - 1)]

                            b = rsglobal.SERVER_RAM_BYTENUM_R[got.ramId]
                            n = got.id

                            o.writeByte(b)
                            o.writeString(n)
                        else:
                            prefer = None
                            for q in self.server_list:
                                if q.type.lower() == t and len(q.players) < q.maxplayers and (ram + idd) != q.fullId:
                                    prefer = q
                                    break
                            else:
                                n = json.load(open("programs\\start_instance.json"))[t]
                                for i in n:
                                    mainWorld = i.get("template", {"world": None}).get("world")
                                    mainWorldNether = i.get("template", {"world_nether": None}).get("world_nether")
                                    mainWorldEnd = i.get("template", {"world_the_end": None}).get("world_the_end")
                                    seed = i.get("seed", None)
                                    if mainWorld == "!random-bridge":
                                        k = [x[0] for x in os.walk("templates\\_worlds") if
                                             len(x[0].split("\\")) == 3 and x[0].split("\\")[2].startswith("_world_bridge")]
                                        random.shuffle(k)
                                        mainWorld = k[0].split("\\")[2]
                                    elif mainWorld == "!smpsaved":
                                        mainWorld = "_world_smpsaved"
                                        mainWorldNether = "_world_nether_smpsaved"
                                        mainWorldEnd = "_world_the_end_smpsaved"
                                        seed = 114514
                                    elif mainWorld == "!buildpublic":
                                        mainWorld = "_world_buildpublic"
                                    
                                    s = rsglobal.DynamicServer(i.get("version", "standard-1.8.8"), "S",
                                                               world=mainWorld,
                                                               world_nether=mainWorldNether,
                                                               world_the_end=mainWorldEnd,
                                                               maxplayers=i.get("maxplayers", 16),
                                                               ram=i.get("ram", 256),
                                                               type=i.get("type", t),
                                                               plugins=i.get("plugins", []),
                                                               seed=seed,
                                                               use_default_plugins=i.get("use_default_plugins", True))
                                    prefer = s
                                    self.server_list.append(s)
                                    s.startUp()
                                    self.LOG.info("Starting up new instance because no warps... " + str(s))

                            # TODO add player amount check

                            self.subawaitwarp.append([nam, prefer.fullId])
                            self.LOG.info(self.subawaitwarp)

                        con.send(OutPacketGroup([o]).data.data)
                        con.close()
                        self.info["tx"] += 1
                        self.info["cx"] += 1
                        continue


                if typ == 0xa1:
                    ram = packet.readByte()
                    idd = packet.readString()
                    t = packet.readByte()
                    msg = packet.readString()

                    if t == 0:
                        l = "INFO"
                    elif t == 1:
                        l = "WARNING"
                    else:
                        l = "ERROR"
                    
                    for i in self.server_list:
                        if i.id == idd:
                            i.logs.append({"time": time.time(), "level": l, "msg": msg})
                            break

                    con.send(OutPacketGroup([]).data.data)
                    con.close()
                    continue

                if typ == 0xae:
                    ram = packet.readByte()
                    idd = packet.readString()
                    for i in self.server_list:
                        if i.id == idd:
                            i.status = "STOPPED"
                            self.server_list.remove(i)
                            break
                    con.send(OutPacketGroup([]).data.data)
                    con.close()

                    crt = OutPacket(0xe3)
                    crt.writeByte(ram)
                    crt.writeString(idd)
                    self.bungee.queued.append(crt)
                    
                    continue
                
                if typ == 0xf0:
                    ram = packet.readByte()
                    sid = packet.readString()
                    nam = packet.readString()
                    tps = float(packet.readString())
                    ramuse = packet.readLong()
                    players = packet.readTypeArray()
                    for i in self.server_list:
                        if i.id == sid:
                            i.name = nam
                            i.players = players     
                            i.ramused = ramuse
                            i.lastping = time.time()
                            i.tps = tps
                            break
                    else:
                        pack = OutPacket(0xc4)
                        pack.writeString("Server Not Found!")
                        con.send(OutPacketGroup([pack]).data.data)
                        con.close()
                        self.info["tx"] += 1
                        continue
                    group = OutPacketGroup(i.queued)
                    self.info["tx"] += 1
                    self.info["cx"] += len(i.queued) + 1
                    con.send(group.data.data)
                    con.close()
                    i.queued = []
                    continue

                if typ == 0xe0:
                    playeramt = packet.readShort()

                    group = OutPacketGroup(self.bungee.queued)
                    con.send(group.data.data)
                    con.close()
                    self.info["tx"] += 1
                    self.info["cx"] += len(self.bungee.queued) + 1
                    self.bungee.queued = []
                    continue

                if typ == 0x83:
                    mode = packet.readByte()
                    if mode == 0x00:

                        self.player_list.append({
                            "name": packet.readString(),
                            "uuid": packet.readString()
                        })
                        print("ADD " + str(self.player_list))
                        con.send(OutPacketGroup([]).data.data)
                        con.close()
                        continue
                    elif mode == 0x01:
                        p = OutPacket(0x83)
                        nam = packet.readString()
                        p.writeString(nam)
                        for i in self.player_list:
                            if i["name"].lower() == nam.lower():
                                p.writeString(i["uuid"])
                                break

                        con.send(OutPacketGroup([p]).data.data)
                        con.close()
                        self.info["tx"] += 1
                        self.info["cx"] += 1
                        continue


                if typ == 0xe1:
                    self.LOG.info("BungeeCord is ready!")
                    con.send(OutPacketGroup([]).data.data)
                    con.close()

                    if "-nolaunch" not in self.argv:
                        self.LOG.info("STARTING AUTO SERVER LAUNCH PROCESS!")
                        self.LOG.info("Loading programs\\start.json...")

                        n = json.load(open("programs\\start.json"))
                        for i in n:
                            a = time.time()

                            mainWorld = i.get("template", {"world": None}).get("world")
                            mainWorldNether = i.get("template", {"world_nether": None}).get("world_nether")
                            mainWorldEnd = i.get("template", {"world_the_end": None}).get("world_the_end")

                            seed = i.get("seed", None)
                            if mainWorld == "!random-bridge":
                                k = [x[0] for x in os.walk("templates\\_worlds") if
                                     len(x[0].split("\\")) == 3 and x[0].split("\\")[2].startswith("_world_bridge")]
                                random.shuffle(k)
                                mainWorld = k[0].split("\\")[2]
                            elif mainWorld == "!smpsaved":
                                mainWorld = "_world_smpsaved"
                                mainWorldNether = "_world_nether_smpsaved"
                                mainWorldEnd = "_world_the_end_smpsaved"
                                seed = 114514
                            elif mainWorld == "!buildpublic":
                                mainWorld = "_world_buildpublic"
                            
                            s = rsglobal.DynamicServer(i.get("version", "standard-1.8.8"), "S",
                                                       world=mainWorld,
                                                       world_nether=mainWorldNether,
                                                       world_the_end=mainWorldEnd,
                                                       maxplayers=i.get("maxplayers", 16),
                                                       ram=i.get("ram", 256),
                                                       type=i.get("type", "unknown"),
                                                       plugins=i.get("plugins", []),
                                                       use_default_plugins=i.get("use_default_plugins", True),
                                                       seed=seed)
                            self.server_list.append(s)
                            s.startUp()
                            self.LOG.info(
                                f"Created and started {s.fullId} ({round((time.time() - a) * 1000, 2)}ms) " + str(i))
                    else:
                        self.LOG.info("Skipping auto-start process!")

                    continue

                if typ == 0xe2:

                    nam = packet.readString()
                    
                    al = []
                    for i in self.server_list:
                        al.append([i.fullId, len(i.players), i.maxplayers, i.type, i.name])
                    ot = OutPacket(0xe4)
                    ot.writeString(nam)
                    ot.writeShort(len(al))
                    for i in al:
                        ot.writeString(i[0])
                        ot.writeString(i[4])
                        ot.writeShort(i[1])
                        ot.writeShort(i[2])
                        ot.writeString(i[3])
                    con.send(OutPacketGroup([ot]).data.data)
                    self.info["tx"] += 1
                    self.info["cx"] += 1
                    con.close()
                    continue
            except Exception as e:
                n = traceback.format_exc()
                print("[Proxy] Packet " + str(data) + " issued an invalid request!")
                print(n)

            
                    

            con.send(OutPacketGroup([]).data.data)
            con.close()
            continue

