import datetime

class LOGLVL:
    INFO = "I"
    WARNING = "W"
    ERROR = "E"
    FATAL = "F"
    DEBUG = "D"

class Logger:

    def __init__(self, obj):
        self.obj = obj
        self.parentname = "%08X" % id(obj) + "@" + obj.__class__.__module__ + "." + obj.__class__.__name__

    def gettime(self):
        return datetime.datetime.now().strftime("%H:%M:%S")

    def log(self, msg, level):
        print(f"({level}) [{self.gettime()}] <{self.parentname}>: " + str(msg))

    def info(self, msg):
        self.log(msg, LOGLVL.INFO)

    def warn(self, msg):
        self.log(msg, LOGLVL.WARNING)

    def error(self, msg):
        self.log(msg, LOGLVL.ERROR)

    def fail(self, msg):
        self.log(msg, LOGLVL.FATAL)

    def debug(self, msg):
        self.log(msg, LOGLVL.DEBUG)