import tkinter as tk
import os

class ServerBrowser:

    def __init__(self, dynamicserver):
        self.dynamic = dynamicserver

    
import tkinter as tk
import tkinter.font as tkFont
from tkinter import font
from tkinter import ttk
import tkinter.messagebox as tkmsg
import rsglobal
import tasks
import traceback
import proxy
import datetime
import json
import pyperclip

class TemplateViewer:

    def __init__(self, r):
        self.creator = r
        self.root = tk.Tk()
        self.root.geometry("500x293")
        self.root.title("Select a Template")
        self.root.resizable(False, False)

        self.list = tk.Listbox(self.root, height = 18, width = 40)
        self.list.place(x = 0, y = 0)
        self.list.bind("<<ListboxSelect>>", self.clickview)
        self.list.bind("<Double-1>", self.select)

        s = len((os.getcwd() + "\\templates\\_worlds").split(sep = "\\"))
        self.w = [x[0] for x in os.walk(os.getcwd() + "\\templates\\_worlds") if len(x[0].split(sep = "\\")) == s + 1]

        for i in range(len(self.w)):
            self.list.insert(i, self.w[i].split("\\")[-1])

        self.info = tk.Label(self.root, anchor = tk.W)
        self.info.place(x = 260, y =10)
        self.info["text"] = "Select a template from the list to view\n its properties."

    def clickview(self, event):
        item = self.w[event.widget.curselection()[0]]
        data = json.load(open(item + "\\worldmetadata.rsd"))
        self.info["text"] = "Properties of " + str(item.split("\\")[-1]) + "\n" + data["world"]["description"] + "\n\nAuthor: " + data["world"]["author"] + "\nGame: " + data["relation"]["game"]["id"] + ":" + data["relation"]["game"]["variation"] + "\nDimension: " + data["world"]["dimension"]

    def select(self, event):
        a = self.w[event.widget.curselection()[0]]
        world = a.split("\\")[-1]
        self.creator.changeworld(world)
        self.root.destroy()

class VersionViewer:

    def __init__(self, r):
        self.creator = r
        self.root = tk.Tk()
        self.root.geometry("500x293")
        self.root.title("Select a Version")
        self.root.resizable(False, False)

        self.list = tk.Listbox(self.root, height = 18, width = 40)
        self.list.place(x = 0, y = 0)
        self.list.bind("<<ListboxSelect>>", self.clickview)
        self.list.bind("<Double-1>", self.select)

        s = len((os.getcwd() + "\\templates").split(sep = "\\"))
        self.w = [x[0] for x in os.walk(os.getcwd() + "\\templates") if len(x[0].split(sep = "\\")) == s + 1]

        for i in range(len(self.w)):
            self.list.insert(i, self.w[i].split("\\")[-1])

        self.info = tk.Label(self.root, anchor = tk.W)
        self.info.place(x = 260, y =10)
        self.info["text"] = "Select a version from the list."

    def clickview(self, event):
        pass
        # item = self.w[event.widget.curselection()[0]]
        # data = json.load(open(item + "\\worldmetadata.rsd"))
        # self.info["text"] = "Properties of " + str(item.split("\\")[-1]) + "\n" + data["world"]["description"] + "\n\nAuthor: " + data["world"]["author"] + "\nGame: " + data["relation"]["game"]["id"] + ":" + data["relation"]["game"]["variation"] + "\nDimension: " + data["world"]["dimension"]

    def select(self, event):
        a = self.w[event.widget.curselection()[0]]
        world = a.split("\\")[-1]
        self.creator.changeversion(world)
        self.root.destroy()

class PluginViewer:

    def __init__(self, r):
        self.creator = r
        self.root = tk.Tk()
        self.root.geometry("500x293")
        self.root.title("Select plugins")
        self.root.resizable(False, False)

        self.list = tk.Listbox(self.root, height = 18, width = 40, selectmode="multiple")
        self.list.place(x = 0, y = 0)

        self._sb = 1
        self.sb = tk.IntVar(value=1)
        self.b = tk.Button(self.root, text="Select", command=self.select)
        self.b.place(x = 260, y = 250)

        self.r = tk.Checkbutton(self.root, text="Use Default Plugins", command=self.n, variable=self.sb, onvalue=1, offvalue=0)
        self.r.place(x = 260, y = 200)
        self.r.select()

        s = len((os.getcwd() + "\\templates\\_plugins").split(sep = "\\"))
        self.w = [x[2] for x in os.walk(os.getcwd() + "\\templates\\_plugins")][0]

        for i in range(len(self.w)):
            self.list.insert(i, self.w[i].split("\\")[-1])

        self.info = tk.Label(self.root, anchor = tk.W)
        self.info.place(x = 260, y =10)
        self.info["text"] = "Select 1 or more plugins.\nDrag select to select multiple plugins.\n\nRSBundler (1.8) plugin will be automatically\nincluded.\nViaversion plugin will be automatically\nincluded."

    def n(self):
        if self._sb == 1: self._sb = 0
        else: self._sb = 1

        if self._sb == 1:
            self.info[
                "text"] = "Select 1 or more plugins.\nDrag select to select multiple plugins.\n\nRSBundler (1.8) plugin will be automatically\nincluded.\nViaversion plugin will be automatically\nincluded."
        else:
            self.info[
                "text"] = "Select 1 or more plugins.\nDrag select to select multiple plugins.\n\nViaversion plugin will be automatically\nincluded."

    def select(self):
        p = []
        for i in self.list.curselection():
            p.append(self.list.get(i))
        self.creator.changeplugins(p, self._sb)
        self.root.destroy()

class CreateNew:
    def __init__(self, home, servers, bungee):
        self.servers = servers
        #setting title
        self.home = home
        self._world = "_world_test1"
        self.bungee = bungee
        root = tk.Tk()
        self.root = root
        self._version = "standard-1.8.8"
        self.plugins = []
        self.usedef = True
        root.title("Create Server")
        #setting window size
        width=500
        height=700
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d' % (width, height)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        GLabel_469=tk.Label(root, font = ("Arial bold", 14))
        GLabel_469["anchor"] = "w"
        #ft = tkFont.Font(family="Lucida", size=14, weight = "bold")
        #GLabel_469["font"] = ft
        GLabel_469["justify"] = "left"
        GLabel_469["text"] = "Create Server"
        GLabel_469.place(x=10,y=10,width=285,height=30)

        GLabel_588=tk.Label(root, wraplengt = 475)
        GLabel_588["anchor"] = "w"
        GLabel_588["justify"] = "left"
        GLabel_588["text"] = "This portion of the operator will be responsible with creating servers manually. Please follow the directions below to create a server.\nIf you need help with parameter operators, go to Help > Args."
        GLabel_588.place(x=10,y=40,width=476,height=50)

        sep = ttk.Separator(root, orient='horizontal')
        sep.place(x=0, y = 100, width = 501)

        n=tk.Label(root, wraplengt = 475, font = ("arial bold", 10))
        n["anchor"] = "w"
        n["justify"] = "left"
        n["text"] = "General Settings"
        n.place(x=10,y=110,width=476,height=30)

        cz=tk.Label(root, wraplengt = 475)
        cz["anchor"] = "w"
        cz["justify"] = "left"
        cz["text"] = "Edit the general settings of the server."
        cz.place(x=10,y=130,width=501,height=30)

        sb=tk.Label(root, wraplengt = 475)
        sb["anchor"] = "w"
        sb["justify"] = "left"
        sb["text"] = "Name"
        sb.place(x=10,y=130,width=501,height=30)

        self.name=tk.Entry(root)
        self.name.place(x=80,y=135,width=370,height=20)
        self.name.insert(0, "-auto")

        sb=tk.Label(root, wraplengt = 475)
        sb["anchor"] = "w"
        sb["justify"] = "left"
        sb["text"] = "Server ID"
        sb.place(x=10,y=160,width=501,height=30)

        self.sid=tk.Entry(root)
        self.sid.place(x=80,y=165,width=370,height=20)
        self.sid.insert(0, "-default")

        sb=tk.Label(root, wraplengt = 475)
        sb["anchor"] = "w"
        sb["justify"] = "left"
        sb["text"] = "RAM (MB)"
        sb.place(x=10,y=190,width=501,height=30)

        self.GLineEdit_163=tk.Entry(root)
        self.GLineEdit_163.place(x=80,y=195,width=370,height=20)
        self.GLineEdit_163.insert(0, "256")

        sb=tk.Label(root, wraplengt = 475)
        sb["anchor"] = "w"
        sb["justify"] = "left"
        sb["text"] = "Target Port"
        sb.place(x=10,y=220,width=501,height=30)

        GLineEdit_163=tk.Entry(root)
        GLineEdit_163.place(x=80,y=225,width=370,height=20)
        GLineEdit_163.insert(0, "-random")

        sb=tk.Label(root, wraplengt = 475)
        sb["anchor"] = "w"
        sb["justify"] = "left"
        sb["text"] = "Server Type"
        sb.place(x=10,y=250,width=501,height=30)

        self.typ=tk.Entry(root)
        self.typ.place(x=80,y=255,width=370,height=20)
        self.typ.insert(0, "verify")

        n=tk.Label(root, wraplengt = 475, font = ("arial bold", 10))
        n["anchor"] = "w"
        n["justify"] = "left"
        n["text"] = "Advanced Settings"
        n.place(x=10,y=290,width=476,height=30)

        GLabel_588=tk.Label(root, wraplengt = 475)
        GLabel_588["anchor"] = "w"
        GLabel_588["justify"] = "left"
        GLabel_588["text"] = "Advanced settings allows you to customize the server's group tags, properties, and other."
        GLabel_588.place(x=10,y=320,width=476,height=15)

        GButton_301=tk.Button(root)
        GButton_301["justify"] = "center"
        GButton_301["text"] = "Edit Group Tags"
        GButton_301.place(x=10,y=350,width=100,height=25)

        GLabel_588=tk.Label(root, wraplengt = 475)
        GLabel_588["anchor"] = "w"
        GLabel_588["justify"] = "left"
        GLabel_588["text"] = "Edit server's role in a group."
        GLabel_588.place(x=120,y=355,width=330,height=15)

        GButton_301=tk.Button(root)
        GButton_301["justify"] = "center"
        GButton_301["text"] = "Properties"
        GButton_301.place(x=10,y=380,width=100,height=25)

        GLabel_588=tk.Label(root, wraplengt = 475)
        GLabel_588["anchor"] = "w"
        GLabel_588["justify"] = "left"
        GLabel_588["text"] = "Edit server's properties file. Not changeable after made."
        GLabel_588.place(x=120,y=385,width=330,height=15)

        GButton_301=tk.Button(root, command=self.selectplugs)
        GButton_301["justify"] = "center"
        GButton_301["text"] = "Plugins"
        GButton_301.place(x=10,y=410,width=100,height=25)

        self.GGLabel_588=tk.Label(root, wraplengt = 475)
        self.GGLabel_588["anchor"] = "w"
        self.GGLabel_588["justify"] = "left"
        self.GGLabel_588["text"] = "Edit server's default plugins. " + str(self.plugins)
        self.GGLabel_588.place(x=120,y=415,width=330,height=15)

        self.GButton_301=tk.Button(root, command = self.selecttemp)
        self.GButton_301["justify"] = "center"
        self.GButton_301["text"] = "Template"
        self.GButton_301.place(x=10,y=440,width=100,height=25)

        self.GLabel_588=tk.Label(root, wraplengt = 475)
        self.GLabel_588["anchor"] = "w"
        self.GLabel_588["justify"] = "left"
        self.GLabel_588["text"] = "Select a template for the server. (" + self._world + ")"
        self.GLabel_588.place(x=120,y=445,width=330,height=15)

        self._btv = tk.Button(root, command=self.selectver)
        self._btv["justify"] = "center"
        self._btv["text"] = "Version"
        self._btv.place(x=10, y=470, width=100, height=25)

        self._v = tk.Label(root, wraplengt=475)
        self._v["anchor"] = "w"
        self._v["justify"] = "left"
        self._v["text"] = "Select a server version (" + self._version + ")"
        self._v.place(x=120, y=475, width=330, height=15)

        sep = ttk.Separator(root, orient='horizontal')
        sep.place(x=0, y = 655, width = 501)

        c=tk.Button(root, command = lambda: root.destroy())
        c["justify"] = "center"
        c["text"] = "Cancel"
        c.place(x=10,y=665,width=100,height=25)

        d=tk.Button(root, command = lambda: self.create())
        d["justify"] = "center"
        d["text"] = "Create"
        d.place(x=390,y=665,width=100,height=25)

        d=tk.Button(root, state = "disabled")
        d["justify"] = "center"
        d["text"] = "Add Later"
        d.place(x=280,y=665,width=100,height=25)

        root.mainloop()

    def selecttemp(self):
        self._viewer_template = TemplateViewer(self)

    def selectver(self):
        self._ver_template = VersionViewer(self)

    def selectplugs(self):
        self._plug_temp = PluginViewer(self)

    def changeworld(self, world):
        self._world = world
        self.GLabel_588["text"] = "Select a template for the server. (" + self._world + ")"

    def changeversion(self, ver):
        self._version = ver
        self._v["text"] = "Select a server version (" + self._version + ")"

    def changeplugins(self, ver, use):
        self.plugins = ver
        self.usedef = bool(use - 1)
        self.GGLabel_588["text"] = "Plugins: " + str(self.plugins)

    def create(self):

        _AUTO_NAME = False
        _AUTO_ID = False

        if len(self.sid.get()) != 4 and self.sid.get() != "-default" :
            tkmsg.showerror("Unable to Create Server", "Server ID be exactly 4 characters long!")
            return
        
        warn = False
        warntext = "You have the following arguments inserted to some of your inputs:\n\n"
        #chek name
        name = self.name.get()
        if name == "-auto":
            warn = True
            _AUTO_NAME = True
            warntext += "Name: [-auto] Auto Name will be generated\n"
            
        c = self.sid.get()
        if c == "-default":
            warn = True
            _AUTO_ID = True
            warntext += "Server ID: [-default] Server ID will be auto generated\n"

        args = {}
        if warn:
            warntext += "\nMake sure all of the optimized arguments are correct. Incorrect arguments might cause server errors. Check before you proceed!"
            x = tkmsg._show("Proceed?", warntext, tkmsg.WARNING, tkmsg.OKCANCEL)
            if x == "cancel":
                return
        if not _AUTO_NAME:
            args["name"] = name
        if not _AUTO_ID:
            args["sid"] = c

        args["type"] = self.typ.get()

        args["ram"] = int(self.GLineEdit_163.get())

        args["world"] = self._world

        args["plugins"] = self.plugins
        args["use_default_plugins"] = self.usedef

        try:
            s = rsglobal.DynamicServer(self._version, "S", **args)
        except Exception as e:
            tkmsg.showerror("Unable to Create Server", "An problem occured while creating server: " + str(e) + "\n\n" + traceback.format_exc())
            return

        s.startUp()
        self.root.destroy()
        self.home.append(s)
        tasks._task_update_server_list(self.servers, self.home)

class Details:
    def __init__(self, dedicated, li):
        self.l = li
        self.root = tk.Tk()
        self.nb = ttk.Notebook(self.root)

        self.basic = ttk.Frame(self.nb)
        self.nb.add(self.basic, text = "General Information")

        self.players = ttk.Frame(self.nb)
        self.nb.add(self.players, text = "Player Details")

        self.log = ttk.Frame(self.nb)
        self.nb.add(self.log, text = "Live Log")

        self.nb.place(x=1, y=1, width=800, height=500)
        
        self.server = dedicated
        #setting title
        self.root.title("[RS-" + self.server.fullId + "] Server Details")
        #setting window size
        width=800
        height=500
        alignstr = '%dx%d' % (width, height)
        self.root.geometry(alignstr)
        self.root.resizable(width=False, height=False)

        self.GLabel_152=tk.Label(self.basic)
        self.GLabel_152["justify"] = "left"
        self.GLabel_152["text"] = "Server ID: [RS-" + self.server.fullId + "]"
        self.GLabel_152.pack()

        self.Label3=tk.Label(self.basic)
        self.Label3["justify"] = "left"
        self.Label3["text"] = "Server Name: " + self.server.name
        self.Label3.pack()

        self.Label7=tk.Label(self.basic)
        self.Label7["justify"] = "left"
        self.Label7["text"] = "Server Port: #" + str(self.server.port)
        self.Label7.pack()

        self.Label4=tk.Label(self.basic)
        self.Label4["justify"] = "left"
        self.Label4["text"] = "Server TPS: " + str(self.server.tps)
        self.Label4.pack()

        self.Label5=tk.Label(self.basic)
        self.Label5["justify"] = "left"
        c = 0
        for i in self.server.players:
            if i[3]:
                c += 1
        self.Label5["text"] = "Server Players: " + str(len(self.server.players)) + "/" + str(self.server.maxplayers) + " (" + str(c) + " Moderator Players)"
        self.Label5.pack()

        self.Label6=tk.Label(self.basic)
        self.Label6["justify"] = "left"
        self.Label6["text"] = "Server RAM Usage: " + str(self.server.ramused) + " MB"
        self.Label6.pack()

        self.Label8=tk.Label(self.basic)
        self.Label8["justify"] = "left"
        self.Label8["text"] = "Server World Name: " + str(self.server.world)
        self.Label8.pack()


        self.player_list = ttk.Treeview(self.players, columns = ("rank", "name", "uuid"), show="headings", selectmode="browse", height = 16)
        self.player_list.heading("rank", text="Rank")
        self.player_list.column("rank", width = 50)
        self.player_list.heading("name", text="Name")
        self.player_list.column("name", width = 100)
        self.player_list.heading("uuid", text="UUID")
        self.player_list.column("uuid", width = 650)
        self.player_list.pack(fill = "both")
        self.player_list.bind("<Button-3>", self.player_right_click)

        self.logs = ttk.Treeview(self.log, columns = ("time", "level", "message"), show="headings", selectmode="browse", height = 16)
        self.logs.heading("time", text="Time")
        self.logs.column("time", width = 50)
        self.logs.heading("level", text="Level")
        self.logs.column("level", width = 50)
        self.logs.heading("message", text="Message")
        self.logs.column("message", width = 700)
        self.logs.pack(fill = "both")
        for i in self.server.logs:
            self.logs.insert('', tk.END, values=(datetime.datetime.fromtimestamp(i["time"]).strftime("%H:%M:%S"), i["level"], i["msg"]))

        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.root.after(1000, self.update)
        #self.root.mainloop()

    def update(self):
        self.Label3["text"] = "Server Name: " + self.server.name
        self.Label4["text"] = "Server TPS: " + str(round(self.server.tps, 2))
        c = 0
        for x in self.server.players:
            if x[3]:
                c += 1
        self.Label5["text"] = "Server Players: " + str(len(self.server.players)) + "/" + str(self.server.maxplayers) + " (" + str(c) + " Moderator Players)"
        self.Label6["text"] = "Server RAM Usage: " + str(self.server.ramused) + " MB"

        for item in self.player_list.get_children():
            tt = self.player_list.item(item)
            for p in self.server.players:
                if tt["values"][2] == p[2]:
                    break
            else:
                self.player_list.delete(item)


        for p in self.server.players:
            for item in self.player_list.get_children():
                tt = self.player_list.item(item)
                if tt["values"][2] == p[2]:
                    break
            else:
                self.player_list.insert('', tk.END, values=(p[3], p[0], p[2]))
        
        self.root.after(1000, self.update)

    def player_right_click(self, event):
        item = self.player_list.item(self.player_list.focus())["values"]
        if item == '':
            allow = "disabled"
        else:
            allow = "normal"
        m = tk.Menu(self.root, tearoff = 0)
        m.add_command(label = "Kick selected player", command = lambda: self.kick_player(item[1]), state = allow)
        m.add_command(label = "Copy Player UUID", command = lambda: pyperclip.copy(item[2]), state = allow)
        m.add_command(label = "Copy Raw UUID", command = lambda: pyperclip.copy(item[2].replace("-", "")), state = allow)
        m.tk_popup(event.x_root, event.y_root)
        m.grab_release()

    def kick_player(self, name):
        pack = proxy.OutPacket(0xb0)
        pack.writeString(name)
        pack.writeString("\u00a7cYou are kicked from the server!")
        self.server.queued.append(pack)

    def on_exit(self):
        self.root.destroy()

if __name__ == "__main__":
    n = tk.Tk()
    x = CreateNew(n)
    n.mainloop()
