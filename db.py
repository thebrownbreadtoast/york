import sqlite3
import time
import os


class YorkDB:
    def __init__(self):
        self.conn = sqlite3.connect(os.getenv("DB_PATH"))

        self.cursor = self.conn.cursor()

        self.create_tables()
    
    def create_tables(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, chat_id INTEGER NOT NULL);")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS chapters (id INTEGER PRIMARY KEY AUTOINCREMENT, chapter_id INTEGER NOT NULL, title TEXT NOT NULL);")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS cron (id INTEGER PRIMARY KEY AUTOINCREMENT, offset_timestamp INTEGER NOT NULL);")

        self.conn.commit()

    def add_user(self, username, chat_id):
        existing_user = self.get_user(username, chat_id)

        if existing_user:
            return

        self.cursor.execute(f"INSERT INTO users (username, chat_id) VALUES ('{username}', {chat_id});")

        self.conn.commit()

    def remove_user(self, username, chat_id):
        self.cursor.execute(f"DELETE FROM users WHERE username = '{username}' AND chat_id = {chat_id};")

        self.conn.commit()
    
    def get_users(self):
        self.cursor.execute("SELECT * FROM users;")

        return self.cursor.fetchall()
    
    def get_user(self, username, chat_id):
        self.cursor.execute(f"SELECT * FROM users WHERE username = '{username}' AND chat_id = {chat_id};")

        return self.cursor.fetchone()
    
    def add_chapter(self, chapter_id, title):
        self.cursor.execute(f"INSERT INTO chapters (chapter_id, title) VALUES ({chapter_id}, '{title}');")

        self.conn.commit()
    
    def get_last_chapter(self):
        self.cursor.execute("SELECT * FROM chapters ORDER BY id DESC LIMIT 1;")

        return self.cursor.fetchone()

    def add_or_update_offset(self):
        self.cursor.execute("SELECT * FROM cron;")

        existing_offset = self.cursor.fetchone()

        offset = int(time.time())

        if existing_offset:
            self.cursor.execute(f"UPDATE cron SET offset_timestamp = {offset};")
        else:
            self.cursor.execute(f"INSERT INTO cron (offset_timestamp) VALUES ({offset});")

        self.conn.commit()

    def get_offset(self):
        self.cursor.execute("SELECT * FROM cron;")

        return self.cursor.fetchone()
