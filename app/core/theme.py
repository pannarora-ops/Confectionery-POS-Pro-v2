"""
Theme Manager
"""

from kivymd.app import MDApp

from app.core.config import DEFAULT_THEME

from app.core.config import PRIMARY_PALETTE


class ThemeManager:

    @staticmethod
    def load(app: MDApp):

        app.theme_cls.theme_style = DEFAULT_THEME

        app.theme_cls.primary_palette = PRIMARY_PALETTE