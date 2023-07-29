
import actions
import os
import shutil
import random
import propertyreader
import json
import subprocess
import threading
import base64
import tkinter as tk
import tkinter.messagebox as tkmsg
import winsound
import time
import proxy
import json

"""
RS GLOBAL LIBRARY
"""

class SERVER_RAM_ID:
    TINY = "T"
    SMALL = "S"
    MEDIUM = "M"
    BIG = "B"
    GIGANTIC = "G"

class SERVER_RAM_NAME:
    TINY = "tiny"
    SMALL = "small"
    MEDIUM = "medium"
    BIG = "big"
    GIGANTIC = "gigantic"

    def get_by_name(n):
        for i in SERVER_RAM_NAME.__dict__:
            if i.lower().startswith(n.lower()):
                return object.__getattribute__(SERVER_RAM_NAME, i)
        return None

SERVER_RAM_BYTENUM = {0: SERVER_RAM_ID.TINY, 1: SERVER_RAM_ID.SMALL, 2: SERVER_RAM_ID.MEDIUM, 3: SERVER_RAM_ID.BIG, 4: SERVER_RAM_ID.GIGANTIC}
SERVER_RAM_BYTENUM_R = {SERVER_RAM_ID.TINY: 0, SERVER_RAM_ID.SMALL: 1, SERVER_RAM_ID.MEDIUM: 2, SERVER_RAM_ID.BIG: 3, SERVER_RAM_ID.GIGANTIC: 4}

class SERVER_TEMPLATES:
    STANDARD_1_8_8 = "standard-1.8.8"

class SERVER_STATUS:
    HIBERNATING = "HIBERNATING"
    SETUP = "SETUP"
    LOADING = "LOADING"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"

class UnsupportedOperationException(Exception):
    """Raised when a class are not supported to perform the targeted operation"""

    def __init__(self, message = None):
        if message == None:
            self.message = "Unsupported Operation"
        else:
            self.message = "Unsupported Operation: " + message
        super().__init__(self.message)

class PopRuntimeError:

    def __init__(self, title, content):
        self.title = title
        self.content = content

    def show(self):
        def b(title, content):
            winsound.Beep(500, 1000)
        def c(title, content):
            window = tk.Tk()
            window.geometry("500x800")
            window.title("Relizc Network Monitor: RW - " + content)

            title = tk.Label(window, text = "loser")
            title.pack()

            window.mainloop()
        x = threading.Thread(target = b, args = (self.title, self.content))
        x.start()
        y = threading.Thread(target = c, args = (self.title, self.content))
        y.start()

        

class Alert:

    def warning(title, message):
        play = True
        def bep(ok):
                time.sleep(0.5)
        x = threading.Thread(target = bep, args=  (play,))
        x.start()
        time.sleep(5)
        play = False
        print("L")

class DynamicServer:

    def format_players(self):
        ap = 0
        for p in self.players:
            if p[3]:
                ap += 1
        return str(len(self.players)) + "/" + str(self.maxplayers) + " (" + str(ap) + ")"

    def __init__(self, version: str, ramId: str = "S", **kwargs):
        self.id = kwargs.get("sid", actions.generateID(4))
        self.ramId = ramId
        self.status = SERVER_STATUS.HIBERNATING
        self.version = version
        self.world = kwargs.get("world", None)
        self.world_nether = kwargs.get("world_nether", None)
        self.world_the_end = kwargs.get("world_the_end", None)
        self.seed = kwargs.get("seed", "")
        self.port = -1

        self.players = []
        self.maxplayers = kwargs.get("maxplayers", 20)
        if kwargs.get("use_default_plugins", True):
            self.plugins = ["RSBundler-1.0.0.jar", "RSViaVer.jar"]
        else:
            self.plugins = ["RSViaVer.jar"]

        for i in kwargs.get("plugins", []):
            self.plugins.append(i)

        self.ramused = 0
        self.maxram = kwargs.get("ram", 256)

        if self.maxram < 256:
            self.ramId = "T"
        elif self.maxram < 512:
            self.ramId = "S"
        elif self.maxram < 1024:
            self.ramId = "M"
        elif self.maxram < 8192:
            self.ramId = "B"
        else:
            self.ramId = "G"

        self.lastping = time.time()
        self.tps = 0
        
        self.type = kwargs.get("type", "unknown")
        self.process = None
        self.att = kwargs.get("attitude", "Normal")
        self.logs = []
        self.queued = []

        if kwargs.get("handleFile", True):
            data = json.load(open("running.json"))

            while True:
                ok = random.randint(128, 32767)
                if ok not in data["usedPorts"].keys():
                    break
            self.port = ok

            data["usedPorts"][self.fullId] = self.port
            json.dump(data, open("running.json", "w"))

            DynamicServer._copyServer(version, self.fullId)
            DynamicServer._copyProperty(version, self.fullId)
            if self.world is not None:
                DynamicServer._copyWorld(self.world, "world", self.fullId)
            if self.world_nether is not None:
                DynamicServer._copyWorld(self.world_nether, "world_nether", self.fullId)
            if self.world_the_end is not None:
                DynamicServer._copyWorld(self.world_the_end, "world_the_end", self.fullId)

            os.makedirs("running\\" + self.fullId + "\\plugins")

            for i in self.plugins:
                self._copyPlugin(i)

            self.name = kwargs.get("name", f"{self.ramId}_{self.id}_{self.version}_{self.type}:" + str(self.port))

            properties = DynamicServer._loadProperty(self.fullId)

            properties.put("server-port", self.port)
            properties.put("max-players", self.maxplayers)
            properties.put("sid", self.id)
            properties.put("rid", self.ramId)
            properties.put("version", self.version)
            properties.put("type", self.type)
            properties.put("name", self.name)
            properties.put("level-seed", self.seed)
            properties.save()

            blob = open(os.getcwd() + "\\running\\" + self.fullId + "\\startup-python.bat", "r").read()
            blob = blob.replace("<RAM>", str(self.maxram))
            f = open(os.getcwd() + "\\running\\" + self.fullId + "\\startup-python.bat", "w")
            f.write(blob)
            f.close()

            
        

        self.status = SERVER_STATUS.HIBERNATING

    def __repr__(self):
        s = []
        for i in self.__dict__:
            s.append(i + "=" + str(self.__dict__[i]))
        return "DynamicServer(" + ", ".join(s) + ")"

    def startUp(self) -> int:
        self.process = subprocess.Popen("startup-python.bat", stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True, cwd='running\\' + self.fullId)
        self.status = SERVER_STATUS.LOADING

    def sendCommand(self, command: str) -> str:
        if self.status != "RUNNING":
            _ = UnsupportedOperationException
            raise _(
                "@DynamicServer.sendCommand WHILE #DynamicServer.status NOT_EQ str(RUNNING)")
        self.process.stdin.write(bytes(command + "\r\n", "ascii"))
        self.process.stdin.flush()
        f = open("running\\" + self.fullId + "\\logs\\latest.log").readlines()
        return f

    def _loadProperty(serverId: str) -> propertyreader.PropertyFile:
        return propertyreader.PropertyFile(open("running\\" + serverId + "\\server.properties")) 

    def _copyServer(templateName: str, serverId:str):
        shutil.copytree("templates\\" + templateName + "\\world", "running\\" + serverId)

    def _copyWorld(worldId: str, dimension: str, serverId: str):
        shutil.copytree("templates\\_worlds\\" + worldId, "running\\" + serverId + "\\" + dimension)
        #os.rename("running\\" + serverId + "\\" + worldId, "running\\" + serverId + "\\" + dimension)

    def _copyPlugin(self, plugin: str):
        shutil.copy("templates\\_plugins\\" + plugin, "running\\" + self.fullId + "\\plugins")

    def _copyProperty(templateName: str, serverId: str):
        shutil.copy("templates\\" + templateName + "\\server.properties", "running\\" + serverId)

    def shutdown(self):
        self.queued.append(proxy.OutPacket(0xaf))

    @property
    def fullId(self):
        return self.ramId + self.id

class BungeeServer:

    def __init__(self, ramId: str = "S", **kwargs):
        self.lastping = time.time()
        self.process = None
        self.att = kwargs.get("attitude", "Normal")
        self.logs = []
        self.queued = []
        self.status = SERVER_STATUS.HIBERNATING

    def __repr__(self):
        s = []
        for i in self.__dict__:
            s.append(i + "=" + str(self.__dict__[i]))
        return "BungeeServer(" + ", ".join(s) + ")"

    def startUp(self) -> int:
        self.process = subprocess.Popen("RUNME.bat", stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True, cwd='bungeecord')
        self.status = SERVER_STATUS.LOADING

    def shutdown(self):
        self.queued.append(proxy.OutPacket(0xaf))
        self.process.stdin.write(bytes("end", "ascii"))
        self.process.kill()

    def sendCommand(self, command: str) -> str:
        if self.status != "RUNNING":
            _ = UnsupportedOperationException
            raise _(
                "@DynamicServer.sendCommand WHILE #DynamicServer.status NOT_EQ str(RUNNING)")
        self.process.stdin.write(bytes(command + "\r\n", "ascii"))
        self.process.stdin.flush()
        f = open("running\\" + self.fullId + "\\logs\\latest.log").readlines()
        return f


if __name__ == "__main__":
    x = PopRuntimeError("1", "1")
    x.show()
    


