from kivy.uix.screenmanager import Screen

from app.core.routes import DASHBOARD


class DashboardScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = DASHBOARD