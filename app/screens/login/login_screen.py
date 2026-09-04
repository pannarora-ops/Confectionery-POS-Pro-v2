from kivy.uix.screenmanager import Screen
from app.core.routes import LOGIN


class LoginScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = LOGIN
        from kivy.uix.screenmanager import Screen
from app.core.routes import LOGIN, DASHBOARD


class LoginScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = LOGIN

    def goto_dashboard(self):
        self.manager.current = DASHBOARD