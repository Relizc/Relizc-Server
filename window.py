import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as tkmsg
import tasks
import time
import windowc
import rsglobal
import proxy
import threading
import os
import subprocess
import sys
import logger
import sys
import json


root = tk.Tk()
LOG = logger.Logger(root)
LOG.info("Initialized Logger!")
root.geometry("1200x704")
root.title("Relizc Network Monitor")
root.resizable(False, False)

servers = ttk.Treeview(root, columns = ("number", "id", "name", "type", "status", "players", "tps", "ram", "att"), show="headings", height=33, selectmode="browse")
servers.tag_configure("warning", foreground="yellow")

servers.heading('number', text='#')
servers.column("number", width=50)
servers.heading('id', text='ID')
servers.column("id", width=100)
servers.heading('name', text='Name')
servers.column("name", width=400)
servers.heading('type', text='Type')
servers.column("type", width=100)
servers.heading('status', text='Status')
servers.column("status", width=100)
servers.heading('players', text='Players')
servers.column("players", width=50)
servers.heading('tps', text='TPS')
servers.column("ram", width=50)
servers.heading('ram', text='RAM Usage')
servers.column("tps", width=50)
servers.heading('att', text='Attitude')
servers.column("att", width=150)

servers.pack(fill = "both")

def servers_rightclick(event):
    item = servers.item(servers.focus())
    if item == '':
        allow = "disabled"
    else:
        allow = "normal"
    m = tk.Menu(root, tearoff = 0)
    m.add_command(label = "Open selected server in file explorer", command = lambda: subprocess.Popen("explorer \"" + os.getcwd() + "\\running\\" + SERVER_LIST[int(item["values"][0]) - 1].fullId + "\""), state = allow)
    m.add_command(label = "Shut down selected server", command = lambda: SERVER_LIST[int(item["values"][0]) - 1].shutdown(), state = allow)
    m.tk_popup(event.x_root, event.y_root)
    m.grab_release()

def click(li):
    sid = li.item(li.selection())["values"][1]
    for i in SERVER_LIST:
        if i.fullId in sid:
            break
    else:
        tkmsg.showerror("Server Monitor", "The server you specified does not exists. Maybe the server was removed? Please check for the server's validation.")
        tasks._task_update_server_list(servers, SERVER_LIST)
        return
    windowc.Details(i, OPEN_DETAILS)

def q():
    global x 
    root.destroy()
    sys.exit()

servers.bind("<Button-3>", servers_rightclick)
servers.bind("<Double-1>", lambda i: click(servers))

menu = tk.Menu(root)
root.config(menu = menu)

menuApp = tk.Menu(menu, tearoff="off")
menuApp.add_command(label="Preferences")
menu.add_cascade(label="Options", menu=menuApp)

menuServerList = tk.Menu(menu, tearoff="off")
menuServerList.add_command(label="Go To Line...", command = lambda: tasks._menu_SrvrList_(servers))
menuServerList.add_separator()
menuServerList.add_command(label="Refresh", command = lambda: tasks._task_update_server_list(servers, SERVER_LIST))
menuServerList.add_command(label="Create New Server", command = lambda: tasks._create_new(servers, SERVER_LIST, BUNGEE))
menuServerList.add_separator()
menuServerList.add_command(label="BungeeCord Options", command = lambda: tasks._bungee(servers, SERVER_LIST))
menuServerList.add_command(label="Kill BungeeCord", command = lambda: BUNGEE.shutdown())
menu.add_cascade(label="Servers", menu=menuServerList)

modApp = tk.Menu(menu, tearoff="off")
modApp.add_command(label="New Ban Record", command=lambda: tasks._menu_createBan())
modApp.add_command(label="New Mute Record")
menu.add_cascade(label="Moderation", menu=modApp)

sg = ttk.Sizegrip(root)
sg.pack(side=tk.RIGHT, anchor="s", padx=0, pady=0)

hint = tk.Label(root, text="Hi im here to help! :)")
hint.pack(side=tk.BOTTOM, anchor="w", padx=0, pady=0)

#tooltips
servers.bind("<Enter>", lambda i: hint.config(text="Server List (Last Updated: " + str(round(time.time() - LAST_UPD)) + " seconds ago)"))
servers.bind("<Leave>", lambda i: hint.config(text=""))

menu.bind("<Enter>", lambda i: hint.config(text="Ugh are you really gonna use these?"))
menu.bind("<Leave>", lambda i: hint.config(text=""))

SERVER_LIST = []
OPEN_DETAILS = []
PLAYER_LIST = []
BUNGEE = None
LAST_UPD = time.time()
server = None
INFO = {"rx": 0, "tx": 0, "cx": 0}

#ticktask
def tick():
    print(SERVER_LIST)
    tasks._task_update_server_list(servers, SERVER_LIST)
    root.after(10000, tick)

def secondtick():
    global root
    root.title("rx: " + str(INFO["rx"]) + " tx: " + str(INFO["tx"]) + " cx: " + str(INFO["cx"]))
    INFO["rx"] = 0
    INFO["tx"] = 0
    INFO["cx"] = 0
    root.after(1000, secondtick)


def upd(t):
    t = time.time()
    tasks._task_update_server_list(servers, SERVER_LIST)
    root.after(10000, lambda: upd(LAST_UPD))

def s(s, SERVER_LIST, BUNGEE, a, q, inf):
    global server
    server = proxy.ProxyListener(s, SERVER_LIST, OPEN_DETAILS, BUNGEE, a, q, inf)

def launch():
    pass

def delete():
    for i in os.listdir("running"):
        if not i in [x.fullId for x in SERVER_LIST]:
            try:
                os.rmdir("running\\" + i)
            except:
                pass
    root.after(60000, delete)

def stop():
    import time
    LOG.info("Closing bungeecord servers...")
    global BUNGEE
    BUNGEE.shutdown()
    LOG.info("Closing all dynamic servers...")
    w = []
    for i in SERVER_LIST:
        w.append(i)
        i.shutdown()
    while True:
        n = 0
        for i in w:
            if i.status != "STOPPED":
                n += 1
        if n == 0: break
        LOG.info(f"Waiting for {n} dynamic servers to close...")
        time.sleep(1)
    LOG.info("No need to terminate I/O thread!")
    LOG.info("Shutting down menu...")
    global root
    root.destroy()
    LOG.info("Closing process complete!")
    sys.exit()

menuApp.add_command(label="Quit Safely", command = stop)

LOG.info("Setting up thread functions...")
root.after(1000, lambda: upd(LAST_UPD))
root.after(1, launch)
root.after(1, delete)
LOG.info("Loading bungeecord servers...")
BUNGEE = rsglobal.BungeeServer()
BUNGEE.startUp()
LOG.info("Completing I/O protocol threading...")
LOG.info("Setting up Protocol Serber")
x = threading.Thread(target = lambda: s(servers, SERVER_LIST, BUNGEE, sys.argv, PLAYER_LIST, INFO))
x.start()
root.after(1, secondtick)


LOG.warn("Autostart will run after bungeecord finished loading!")

LOG.info("Finished auto server creating process!")
LOG.info("All done! Starting mainloop...")
root.mainloop()
