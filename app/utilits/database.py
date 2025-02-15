from loguru import logger
import sqlite3


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def fetchall(self, query: str, params: tuple = ()):
        try:
            self.cursor.execute(query, params)
            return [row[0] for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error executing query: {e}")
            return []

    def fetchall_multiple(self, query: str, params: tuple = ()):
        try:
            self.cursor.execute(query, params)
            return [row for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error executing query: {e}")
            return []

    def execute(self, query: str, params: tuple = ()):
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error executing query: {e}")

    def last_added_id(self, idt):
        try:
            return self.fetchall(f"select id from tasks where idt={idt}")[-1]
        except (sqlite3.Error, IndexError) as e:
            logger.error(f"Error executing query/ Or index error: {e}")

    def close(self):
        self.conn.close()


database = Database("database/db.db")
