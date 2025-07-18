import os
from pathlib import Path
import sqlite3

from database.entity.entity import Entity
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
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})")
        self.conn.commit()

    def list_tables(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [table[0] for table in  self.cursor.fetchall()]

    def insert(self, entity: Entity):
        columns = entity.__dataclass_fields__.keys()
        values = [getattr(entity, col) for col in columns]
        placeholders = ", ".join(["?"] * len(values))
        sql = f"INSERT INTO {entity.table_name()} ({', '.join(columns)}) VALUES ({placeholders})"
        self.cursor.execute(sql, values)
        self.conn.commit()