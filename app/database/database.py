"""
SQLite Database Manager
"""

import sqlite3

from app.core.config import DATABASE_PATH


class Database:

    def __init__(self):

        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

        self.connection = sqlite3.connect(DATABASE_PATH)

        self.connection.row_factory = sqlite3.Row

    def cursor(self):

        return self.connection.cursor()

    def commit(self):

        self.connection.commit()

    def close(self):

        self.connection.close()