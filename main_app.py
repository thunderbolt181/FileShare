import kivy
from kivy.app import App
from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen

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
        with open("prev_details.txt","w") as f:
            f.write(f"{self.ids.ip.text},{self.ids.port.text},{self.ids.username.text}")
        f.close()
        print(f"{self.ids.ip.text},{self.ids.port.text},{self.ids.username.text}")


class WindowManager(ScreenManager):
    pass

kv=Builder.load_file("main_app.kv")

class MyApp(App):
    def build(self):
        return kv

if __name__ == "__main__":
    MyApp().run()