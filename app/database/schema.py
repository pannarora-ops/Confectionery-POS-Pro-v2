"""
Database Schema
"""

from app.database.database import Database


def initialize_database():

    db = Database()

    cursor = db.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            full_name TEXT,

            role TEXT,

            is_active INTEGER DEFAULT 1

        );
        """
    )

    db.commit()

    db.close()