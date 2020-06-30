import kivy
import os
import socket
import time
import queue
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.popup import Popup
from kivy.properties import StringProperty,ObjectProperty
from kivy.uix.gridlayout import GridLayout 
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

#:::::::::::::::::::::::::::::::::::::: GLOBAL VARIABLES :::::::::::::::::::::::::::::::::::::::::::::::::::::::
#  Problem occurs during sending file name and file size
#:::::::::::::::::::::::::::::::::::::: GLOBAL VARIABLES :::::::::::::::::::::::::::::::::::::::::::::::::::::::

#:::::::::::::::::::::::::::::::::::::: GLOBAL VARIABLES :::::::::::::::::::::::::::::::::::::::::::::::::::::::
q=queue.Queue()
p=queue.Queue()
r=queue.Queue()
files=queue.Queue()
#:::::::::::::::::::::::::::::::::::::: GLOBAL VARIABLES :::::::::::::::::::::::::::::::::::::::::::::::::::::::

#:::::::::::::::::::::::::::::::::::::: RECIVER SOCKET :::::::::::::::::::::::::::::::::::::::::::::::::::::::::

class ReciverSocket:
    def __init__(self,q):
        self.ip=q.get()
        self.port=int(q.get())
        self.username=q.get()
        self.SIZE = 104857600
        self.data_recvd=0
        try:
            self.mysock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.mysock.connect((self.ip, self.port))
            q.put(True)
            print("Connected")
            self.start_transfer()
        except:
            q.put(False)
            p.put(False)
            self.mysock.close()
            print("Cannot Connect")
             
    def start_transfer(self):
        self.filename = self.mysock.recv(2048).decode("utf-8")
        self.mysock.send(bytes("1","utf-8")) 
        self.filesize = self.mysock.recv(2048).decode("utf-8")
        r.put(self.filename)
        time.sleep(1)
        r.put(int(self.filesize)/(1024*1024))
        self.mysock.send(bytes("1","utf-8")) 
        self.start_time = time.time()
        while not p.empty():
            p.get()
        if p.empty():
            self.file = open(f"C:\\Users\\Shivam Baghel\\Desktop\\{self.filename}", "wb")
            while p.empty():
                self.st=time.time()
                self.msg = self.mysock.recv(self.SIZE)
                self.file.write(self.msg)
                self.end=time.time()
                self.data_recvd+=len(self.msg)
                files.put(self.data_recvd/(1024*1024))
                # print(round(len(self.msg)*0.000001 / (self.end - self.st), 3),'MB/sec.',round(self.data_recvd * 0.000001,3))
                if not self.msg:
                    break
            self.d = os.path.getsize(f"C:\\Users\\Shivam Baghel\\Desktop\\{self.filename}")
            # print(self.d*0.000001)
            # print('Total:', self.end - self.start_time)
            # print('Throughput:', round((self.d * 0.000001) / (self.end - self.start_time), 3),'MB/sec.')
            self.file.close()
            p.put(True)
            print("Completed")
            # print('Successfully received the file')
            # print('connection closed')
        self.mysock.close()

#:::::::::::::::::::::::::::::::::::::: RECIVER SOCKET :::::::::::::::::::::::::::::::::::::::::::::::::::::::

#:::::::::::::::::::::::::::::::::::::: SENDER SOCKET ::::::::::::::::::::::::::::::::::::::::::::::::::::::::
class SenderSocket:
    def __init__(self,q,p):
        self.get_ip()
        self.SIZE = 104857600
        self.data_recvd=0
        self.port=1234
        try:
            self.mysock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.mysock.bind((self.IP,self.port))
            q.put(True)
            q.put([self.IP,self.port])
            # print("Connected")
            self.listen_socket()
        except:
            q.put(False)
            self.mysock.close()
            # print("Cannot Connect")

    def listen_socket(self):
        try:
            self.mysock.settimeout(32)
            self.mysock.listen(1)
            # print("[SERVER LISTENING.....]\n")
            # print(f"On the reciving end enter {self.IP}\n")
            self.clientsocket , self.address = self.mysock.accept()
            # print(f"{self.address} is connected")
            q.put(True)
            self.conn()
        except:
            q.put(False)
            # print("timeout")

    def get_ip(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.s.connect(('10.255.255.255', 1))
            self.IP = self.s.getsockname()[0]
            # print(self.s.getsockname())
        except:
            self.IP = '127.0.0.1'
        finally:
            self.s.close()

    def sendfilename(self):
        self.clientsocket.send(bytes(self.filename, "utf-8"))
        self.a=self.clientsocket.recv(2048).decode("utf-8")
        self.clientsocket.send(bytes(str(self.filesize), "utf-8"))
        self.a=self.clientsocket.recv(2048).decode("utf-8")
        if int(self.a):
            pass
        else:
            self.clientsocket.close()

    def conn(self):
        try:
            self.filepath = files.get()
            p.put(True)
        except:
            p.put(False)
            self.clientsocket.close()
            return
        self.filename=self.filepath.split("\\")[-1]
        self.filesize=os.path.getsize(self.filepath)
        time.sleep(1)
        r.put(self.filename)
        time.sleep(1)
        r.put(self.filesize)
        self.sendfilename()
        self.file = open(f"{self.filepath}","rb")
        self.msg = self.file.read(self.SIZE)
        self.data_send=0
        while (self.msg and q.empty()):
            self.st=time.time()
            self.clientsocket.send(bytes(self.msg))
            self.msg=self.file.read(self.SIZE)
            self.end=time.time()
            self.data_send+=len(self.msg)
            r.put(self.data_send)
            # print(round(len(self.msg)*0.000001 / (self.end - self.st), 3),'MB/sec.',round(self.data_send * 0.000001,3))
        q.put(True)
        self.file.close()
        self.clientsocket.close()

#:::::::::::::::::::::::::::::::::::::: SENDER SOCKET ::::::::::::::::::::::::::::::::::::::::::::::::::::::::

#:::::::::::::::::::::::::::::::::::::: SCREENS ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

class MainScreen(Screen):
    pass

class SendScreen(Screen):
    def __init__(self,**kwargs):
        super(SendScreen,self).__init__(**kwargs)

    def on_enter(self):
        t=threading.Thread(target=SenderSocket,args=(q,p),daemon=True)
        t.start()
        Clock.schedule_once(self.check_start_server)

    def check_start_server(self,_):
        self.timeout=30
        if not q.empty():
            if q.get():
                self.ip=q.get()
                self.ids.starting_server.text="SERVER STARTED"
                self.ids.device_ip.text=f"On the RECEIVER'S Device Enter \n  IP: {self.ip[0]} \n  Port: {self.ip[1]}"
                self.ids.server_timeout.text="Time Until Server Timeout"
                self.ids.server_timeout_time.text=f"{self.timeout}"
                Clock.schedule_once(self.change_screen,1)
            else:
                self.ids.starting_server.text="Cannot Start Server"
                self.ids.device_ip.text=f""
                Clock.schedule_once(self.change_screen,1)
        else:
            Clock.schedule_once(self.check_start_server,1)

    def change_screen(self,_):
        if not q.empty():
            if not q.get():
                self.ids.starting_server.text="SERVER TIMEED OUT"
                self.ids.device_ip.text=f""
                self.ids.server_timeout.text=""
                self.ids.server_timeout_time.text=""
                Clock.schedule_once(self.back,1)
            else:
                self.manager.current="SendFile"
                self.manager.transition.direction="right"
                self.ids.starting_server.text="STARTING SERVER"
                self.ids.device_ip.text=f""
                self.ids.server_timeout.text=""
                self.ids.server_timeout_time.text=""
        else:
            self.ids.server_timeout_time.text=f"{self.timeout}"
            self.timeout-=1
            Clock.schedule_once(self.change_screen,1)

    def back(self,_):
        self.manager.current="Main"
        self.manager.transition.direction="right"
        self.ids.starting_server.text="STARTING SERVER"
        self.ids.device_ip.text=f""

class SendFile(Screen):
    def __init__(self,**kwargs):
        super(SendFile,self).__init__(**kwargs)

    def on_enter(self):
        Clock.schedule_once(self.start_sending)
    
    def start_sending(self,_):
        self.ids.file_name_send.text="SELECT A FILE"
        if not p.empty():
            if p.get():
                self.ids.file_name_send.text=f"{r.get()}"
                self.ids.file_size.text=f"{r.get()/(1024*1024)} MB"
                self.ids.file_size_send.text=f"0 MB"
                Clock.schedule_once(self.update_info_send,1)
            else:
                self.manager.current="Main"
                self.manager.transition.direction="left"
                self.ids.file_name_send.text="CONNECTED"
        else:
            Clock.schedule_once(self.start_sending,1)
    
    def update_info_send(self,_):
        if not r.empty() :
            self.blabla=r.get()
            print(self.blabla)
            self.ids.file_size_send.text=f"{self.blabla/(1024*1024)} MB"
            if not q.empty():
                self.ids.file_size_send.text=self.ids.file_size.text
                self.ids.c_btn.text="CONTINUE"
            Clock.schedule_once(self.update_info_send,1)
        else:
            Clock.schedule_once(self.update_info_send,1)

    def cancel_send(self):
        q.put(False)
        self.ids.file_name_send.text=f"CONNECTED"
        self.ids.file_size.text=f""
        self.ids.file_size_send.text=f""
        self.ids.c_btn.text="CANCEL"

class Filechooser(BoxLayout,Screen):
    paths=StringProperty()
    def __init__(self,**kwargs):
        super(Filechooser,self).__init__(**kwargs)
        self.paths="C:/"
        self.select_file_name=""

    def on_enter(self):
        global files
        while not q.empty():
            q.get()
        while not p.empty():
            p.get()
        while not r.empty():
            r.get()
        while not files.empty():
            files.get()
    
    def select(self, *args): 
        try: 
            # print(args[1])
            self.select_file_name=args[1][0]
            files.put(self.select_file_name)
        except: 
            pass

    def selected_files(self,*args):
        if self.select_file_name!="":
            self.manager.current="Send"
            self.manager.transition.direction = 'left'
        else:
            pass

    def popup_btn(self):
        self.drives=[]
        self.drives = [chr(x) for x in range(65,90) if os.path.exists(chr(x) + ":") ]
        self.layout = GridLayout(cols = 1, padding = 10)
        popupwindow=Popup(title="Select Drives",content=self.layout,size_hint=(0.7,0.5))
        popupwindow.open()
        self.drive_list = GridLayout(cols = 2, padding = 10)
        self.layout.add_widget(self.drive_list)
        for i in self.drives:
            self.btn = Button(text=str(i),on_press =self.change_drive,on_release=popupwindow.dismiss)
            self.drive_list.add_widget(self.btn)
        self.cancel_grid=GridLayout(cols=1,padding=5)
        self.layout.add_widget(self.cancel_grid)
        self.cancel_select=Button(text="CANCEL",on_press=popupwindow.dismiss)
        self.cancel_grid.add_widget(self.cancel_select)

    def change_drive(self,instance):
        self.paths=f"{str(instance.text)}:/"

class ReceiveScreen(Screen):
    ip_prev=ObjectProperty(None)
    port_prev=ObjectProperty(None)
    username_prev=ObjectProperty(None)
    def __init__(self, **kwargs):
        super(ReceiveScreen,self).__init__(**kwargs)
        try:
            with open("prev_details.txt","r") as f:
                self.ip_prev,self.port_prev,self.username_prev=f.read().split(",")
            f.close()
        except:
            self.ip_prev,self.port_prev,self.username_prev="","",""

    def try_connect(self):
        if self.ids.ip.text!="" and self.ids.port.text!="" and self.ids.username.text!="":
            with open("prev_details.txt","w") as f:
                f.write(f"{self.ids.ip.text},{self.ids.port.text},{self.ids.username.text}")
            f.close()
        while not q.empty():
            q.get()
        while not p.empty():
            p.get()
        while not r.empty():
            r.get()
        q.put(self.ids.ip.text)
        q.put(self.ids.port.text)
        q.put(self.ids.username.text)
        t=threading.Thread(target=ReciverSocket,args=(q,),daemon=True)
        t.start()

class Recv_Sock_Check(Screen):
    def __init__(self, **kwargs):
        super(Recv_Sock_Check,self).__init__(**kwargs)

    def on_enter(self):
        Clock.schedule_once(self.check,0.5)

    def check(self,_):
        if not q.empty():
            if q.get():
                self.manager.current="ReceivingFile"
                self.manager.transition.direction="left"
            else:
                self.manager.current="Receive"
                self.manager.transition.direction="right"
        else:
            Clock.schedule_once(self.check,1)

class ReceivingFile(Screen):
    def __init__(self, **kwargs):
        super(ReceivingFile,self).__init__(**kwargs)

    def on_enter(self):
        while not r.empty():
            r.get()
        while not files.empty():
            files.get()
        self.ids.file_name.text="RECEIVING FILE INFO"
        self.ids.file_size.text=""
        self.ids.file_size_recvd.text=""
        self.ids.cancel_btn.text="CANCEL"
        Clock.schedule_once(self.close_connection,1)
        Clock.schedule_once(self.update_info,0.5)

    def update_info(self,_):
        if not r.empty():
            self.ids.file_name.text=str(r.get())
            self.ids.file_size.text=f"{r.get()} MB"
            self.ids.file_size_recvd.text="0 MB"
            while not r.empty():
                r.get()
            Clock.schedule_once(self.updating_recvd_size,1)
        else:
            Clock.schedule_once(self.update_info,1)

    def updating_recvd_size(self,_):
        if not files.empty():
            self.ids.file_size_recvd.text=f"{files.get()} MB"
            Clock.schedule_once(self.updating_recvd_size,1)
        else:
            Clock.schedule_once(self.updating_recvd_size,1)

    def close_connection(self,_):
        if not p.empty():
            if not p.get():
                self.manager.current="Receive"
                self.manager.transition.direction="right"
            else:
                self.ids.cancel_btn.text="CONTINUE"
        else:
            Clock.schedule_once(self.close_connection,1)

    def cancel(self):
        p.put(False)
        p.put(False)

#:::::::::::::::::::::::::::::::::::::: SCREENS :::::::::::::::::::::::::::::::::::::::::::::::::::::::

class WindowManager(ScreenManager):
    pass

kv=Builder.load_file("main_app.kv")

class MyApp(App):
    def build(self):
        return kv

if __name__ == "__main__":
    MyApp().run()