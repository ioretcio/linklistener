import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='invite_stats.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

class DatabaseManager:
    def __init__(self, db_path='invite_stats.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS invite_stats_new (
            invite_link TEXT,
            user_id INTEGER,
            username TEXT,
            name TEXT,
            channel TEXT,
            link_createt TEXT,
            time TEXT  -- New column to store the timestamp
        )
        ''')
        self.conn.commit()

    def save_invite(self, invite_link, user_id, username, name, channel, link_created):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('''
        INSERT INTO invite_stats_new (invite_link, user_id, username, name, channel, link_createt, time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (invite_link, user_id, username, name, channel, link_created, current_time))
        self.conn.commit()

    def close(self):
        self.conn.close()
