import kivy
import os
import socket
import time
import queue
import threading
from kivy.clock import Clock
from kivy.app import App
from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen

#:::::::::::::::::::::::::::::::::::::: GLOBAL VARIABLES :::::::::::::::::::::::::::::::::::::::::::::::::::::::
T=None
q=queue.Queue()
p=queue.Queue()
r=queue.Queue()
#:::::::::::::::::::::::::::::::::::::: GLOBAL VARIABLES :::::::::::::::::::::::::::::::::::::::::::::::::::::::

#:::::::::::::::::::::::::::::::::::::: RECIVER SOCKET :::::::::::::::::::::::::::::::::::::::::::::::::::::::::

class ReciverSocket:
    def __init__(self,q):
        self.ip=q.get()
        self.port=int(q.get())
        self.username=q.get()
        self.SIZE = 104857600
        self.data_recvd=0
        # print(self.ip,self.port,self.username)
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
        time.sleep(1)
        self.filename = self.mysock.recv(2048).decode("utf-8")
        self.filesize = self.mysock.recv(2048).decode("utf-8")
        r.put(self.filename)
        r.put(int(self.filesize)/(1024*1024))
        self.mysock.send(bytes("1","utf-8")) 
        self.start_time = time.time()
        if p.empty():
            self.file = open(f"C:\\Users\\Shivam Baghel\\Desktop\\{self.filename}", "wb")
            while p.empty():
                self.st=time.time()
                self.msg = self.mysock.recv(self.SIZE)
                self.file.write(self.msg)
                self.end=time.time()
                self.data_recvd+=len(self.msg)
                r.put(self.data_recvd/(1024*1024))
                print(round(len(self.msg)*0.000001 / (self.end - self.st), 3),'MB/sec.',round(self.data_recvd * 0.000001,3))
                if not self.msg:
                    break
            self.d = os.path.getsize(f"C:\\Users\\Shivam Baghel\\Desktop\\{self.filename}")
            print(self.d*0.000001)
            print('Total:', self.end - self.start_time)
            print('Throughput:', round((self.d * 0.000001) / (self.end - self.start_time), 3),'MB/sec.')
            self.file.close()
            p.put(True)
            print('Successfully received the file')
            print('connection closed')
        self.mysock.close()

#:::::::::::::::::::::::::::::::::::::: RECIVER SOCKET :::::::::::::::::::::::::::::::::::::::::::::::::::::::

#:::::::::::::::::::::::::::::::::::::: SCREENS ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

class MainScreen(Screen):
    pass

class SendScreen(Screen):
    pass

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
        Clock.schedule_once(self.check,2)

    def check(self,_):
        if not q.empty():
            if q.get():
                self.manager.current="ReceivingFile"
                self.manager.transition.direction="left"
            else:
                self.manager.current="Receive"
                self.manager.transition.direction="right"
        else:
            Clock.schedule_once(self.check,2)

class ReceivingFile(Screen):
    def __init__(self, **kwargs):
        super(ReceivingFile,self).__init__(**kwargs)

    def on_enter(self):
        self.ids.file_name.text="RECEIVING FILE INFO"
        self.ids.file_size.text=""
        self.ids.file_size_recvd.text=""
        self.ids.cancel_btn.text="CANCEL"
        Clock.schedule_once(self.close_connection,1)
        Clock.schedule_once(self.update_info,1)

    def update_info(self,_):
        if not r.empty():
            self.ids.file_name.text=str(r.get())
            self.ids.file_size.text=f"{r.get()} MB"
            self.ids.file_size_recvd.text="0 MB"
            Clock.schedule_once(self.updating_recvd_size,1)
        else:
            Clock.schedule_once(self.update_info,1)

    def updating_recvd_size(self,_):
        if not r.empty():
            self.ids.file_size_recvd.text=f"{r.get()} MB"
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
        # if self.ids.cancel_btn.text=="CANCEL":
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