import kivy
from kivy.app import App
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

class MainScreen(Screen):
    pass

class SendScreen(Screen):
    pass

class ReceiveScreen(Screen):
    pass

class WindowManager(ScreenManager):
    pass

kv=Builder.load_file("main_app.kv")

class MyApp(App):
    def build(self):
        return kv

if __name__ == "__main__":
    MyApp().run()