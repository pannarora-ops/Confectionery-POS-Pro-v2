from kivy.clock import Clock
from kivy.uix.screenmanager import Screen

from app.core.routes import SPLASH, LOGIN


class SplashScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = SPLASH

    def on_enter(self):
        Clock.schedule_once(self.next_screen, 2)

    def next_screen(self, *_):
        print("Available screens:", self.manager.screen_names)
        self.manager.current = LOGIN