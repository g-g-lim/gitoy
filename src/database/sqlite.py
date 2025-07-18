import os
from pathlib import Path
import sqlite3

from util.constant import GITOY_DB_FILE, GITOY_DIR


class SQLite:

    def __init__(self):
        self.gitoy_db_path = Path(os.getcwd(), GITOY_DIR, GITOY_DB_FILE)
        self.gitoy_db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn: sqlite3.Connection = sqlite3.connect(self.gitoy_db_path.absolute())
        self.cursor: sqlite3.Cursor = self.conn.cursor()

        self.conn.execute("PRAGMA journal_mode = WAL")
        self.conn.execute("PRAGMA synchronous = NORMAL")
        self.conn.execute("PRAGMA temp_store = MEMORY")

    def create_table(self, table_name: str, columns: list[str]):
        print(table_name, columns)
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})")
        self.conn.commit()

    def list_tables(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [table[0] for table in  self.cursor.fetchall()]