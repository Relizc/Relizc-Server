import random
import os
import shutil

 
def generateID(length):
    r = ""
    for i in range(length):
        r += random.choice([chr(i) for i in range(97, 123)] + list("0123456789"))
            
    return r

def copyServer(templateName: str, serverId: str):
    shutil.copytree("templates\\" + templateName + "\\world", "running\\" + serverId)
