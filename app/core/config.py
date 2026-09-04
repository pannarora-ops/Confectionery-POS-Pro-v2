"""
Application Configuration
"""

from pathlib import Path

# --------------------------------------------------
# App Information
# --------------------------------------------------

APP_NAME = "Confectionery POS Pro v2"
APP_VERSION = "2.0.0-alpha.1"

# --------------------------------------------------
# Project Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

APP_DIR = BASE_DIR / "app"

DATA_DIR = BASE_DIR / "data"

LOG_DIR = DATA_DIR / "logs"

BACKUP_DIR = DATA_DIR / "backups"

DATABASE_PATH = DATA_DIR / "confectionery.db"

# --------------------------------------------------
# UI
# --------------------------------------------------

DEFAULT_THEME = "Light"

PRIMARY_PALETTE = "Blue"

ACCENT_PALETTE = "Amber"

WINDOW_WIDTH = 1200

WINDOW_HEIGHT = 720