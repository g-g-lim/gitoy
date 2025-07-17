import os
from pathlib import Path
import sqlite3

from util.constant import GITOY_DIR


class SQLite:

    def __init__(self):
        self.path = Path(os.getcwd(), GITOY_DIR, "gitoy.db")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: sqlite3.Connection = sqlite3.connect(self.path.absolute())
        self.cursor: sqlite3.Cursor = self.conn.cursor()

        self.conn.execute("PRAGMA journal_mode = WAL")
        self.conn.execute("PRAGMA synchronous = NORMAL")
        self.conn.execute("PRAGMA temp_store = MEMORY")

    def create_table(self, table_name: str, columns: list[str]):
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})")
        self.conn.commit()