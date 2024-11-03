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
        CREATE TABLE IF NOT EXISTS invite_stats (
            invite_link TEXT,
            user_id INTEGER,
            username TEXT,
            name TEXT,
            phone_number TEXT,
            channel TEXT,
            time TEXT  -- New column to store the timestamp
        )
        ''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS channel_links (
            channel TEXT,
            invite_link TEXT,
            spreadsheet_id TEXT,
            UNIQUE(channel, invite_link)
        )
        ''')
        self.conn.commit()

    def save_invite(self, invite_link, user_id, username, name, phone_number, channel):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('''
        INSERT INTO invite_stats (invite_link, user_id, username, name, phone_number, channel, time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (invite_link, user_id, username, name, phone_number, channel, current_time))
        self.conn.commit()

    def get_invite_stats(self):
        self.cursor.execute('SELECT channel, invite_link, COUNT(user_id) FROM invite_stats GROUP BY channel, invite_link')
        return self.cursor.fetchall()

    def save_channel_link(self, channel, invite_link, spreadsheet_id):
        self.cursor.execute('''
        INSERT OR IGNORE INTO channel_links (channel, invite_link, spreadsheet_id)
        VALUES (?, ?, ?)
        ''', (channel, invite_link, spreadsheet_id))
        self.conn.commit()

    def get_channel_links(self):
        self.cursor.execute('SELECT channel, invite_link, spreadsheet_id FROM channel_links')
        return self.cursor.fetchall()
    
    def get_spreadsheet_id_for_channel(self, channel):
        self.cursor.execute('SELECT spreadsheet_id FROM channel_links WHERE channel = ?', (channel,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def close(self):
        self.conn.close()
