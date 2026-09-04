from kivy.uix.screenmanager import ScreenManager
from app.core.screen_registry import SCREENS


class AppScreenManager(ScreenManager):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        for screen_cls in SCREENS:
            screen = screen_cls()
            print(f"Adding: {screen.name}")
            self.add_widget(screen)

        print("Registered:", self.screen_names)
        print("Current:", self.current)