import tkinter as tk
import tkinter.messagebox as tkmsg
import rsglobal
import time
import windowc

_TASKENV_MENU_SRVLIST_BOX_OPEN = False
_TASKENV_MENU_SRVLIST_BOX_VAL = None
_TASKENV_MENU_LASTUPD = time.time()

def _task_update_server_list(servers: "tkinter", serverlist):
    global _TASKENV_MENU_LASTUPD
    for item in servers.get_children():
        servers.delete(item)
    n = 0
    for i in serverlist:
        if i.status == rsglobal.SERVER_STATUS.RUNNING and time.time() - i.lastping > 30:
            tkmsg.showwarning('[RS-' + i.fullId + "] Server Lost Track", "This server was removed from the protocol "
                                                                         "because it didn't ping in the last 30 "
                                                                         "seconds!\n\nPlease check if there is an "
                                                                         "error, and try and patch it.")
            serverlist.remove(i)
            continue
        n += 1
        servers.insert('', tk.END, values=(str(n), '[RS-' + i.fullId + "]", i.name, i.type, i.status, i.format_players(), str(i.tps), str(i.ramused) + " MB", i.att), text="ERROR", tag = "warning")
    _TASKENV_MENU_LASTUPD = time.time()

def _menu_createBan():
    pass

def _menu_SrvrList_(servers: "tkinter"):
    global _TASKENV_MENU_SRVLIST_BOX_OPEN, _TASKENV_MENU_SRVLIST_BOX_VAL
    
    _TASKENV_MENU_SRVLIST_BOX_OPEN = True
    def a(servers, b, e):
        try:
            n = int(e)
        except:
            tkmsg.showerror("Go To Line...", "Invalid Line Number! Please enter an integer")
            return
        b.destroy()
        servers.yview(n + 1)
        _TASKENV_MENU_SRVLIST_BOX_OPEN = False
        _TASKENV_MENU_SRVLIST_BOX_VAL = None
        
    ask = tk.Tk()
    ask.geometry("300x80")
    ask.title("Go To Line...")
    ask.resizable(False, False)

    _TASKENV_MENU_SRVLIST_BOX_VAL = ask

    l1 = tk.Label(ask, text="Enter Line Number")
    l1.pack()

    e1 = tk.Entry(ask)
    e1.bind("<Return>", lambda i: a(servers, ask, e1.get()))
    e1.pack()

    b1 = tk.Button(ask, text = "Go!", command = lambda: a(servers, ask, e1.get()))
    b1.pack()

def _create_new(servers, l, b):
    windowc.CreateNew(l, servers, b)
    
