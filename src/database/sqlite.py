
import sqlite3

from database.entity.entity import Entity
from util.file_handler import FileHandler


class SQLite:

    def __init__(self, file_handler: FileHandler):
        self.gitoy_db_path = file_handler.get_repo_db_file()

        if self.gitoy_db_path is None:
            self.gitoy_db_path = file_handler.create_repo_db_file()

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

    def select(self, query: str) -> list[dict]:
        self.cursor.execute(query)
        columns = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def update(self, entity: Entity, update_values: dict):
        set_clause = ", ".join([f"{col} = ?" for col in update_values.keys()])
        sql = f"UPDATE {entity.table_name()} SET {set_clause} WHERE {entity.primary_key_column()} = ?"
        values = list(update_values.values())
        values.append(entity.primary_key)
        self.cursor.execute(sql, values)
        self.conn.commit()

    def delete(self, entity: Entity):
        sql = f"DELETE FROM {entity.table_name()} WHERE {entity.primary_key_column()} = ?"
        self.cursor.execute(sql, [entity.primary_key])
        self.conn.commit()