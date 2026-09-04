from kivymd.app import MDApp

from app.core.config import APP_NAME
from app.core.theme import ThemeManager
from app.core.kv_loader import load_all_kv
from app.core.screen_manager import AppScreenManager
from app.database.schema import initialize_database


class ConfectioneryPOSApp(MDApp):

    def build(self):

        self.title = APP_NAME

        ThemeManager.load(self)

        load_all_kv()

        initialize_database()

        return AppScreenManager()