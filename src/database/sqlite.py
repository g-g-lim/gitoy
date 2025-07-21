import sqlite3
from pathlib import Path
from typing import Optional

from database.entity.entity import Entity


class SQLite:

    def __init__(self, path: Path):
        self.path = path
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None

    def connect(self):
        self.conn = sqlite3.connect(self.path.absolute())
        self.cursor = self.conn.cursor()
        self.conn.execute("PRAGMA journal_mode = WAL")
        self.conn.execute("PRAGMA synchronous = NORMAL")
        self.conn.execute("PRAGMA temp_store = MEMORY")
        return self.conn, self.cursor
    
    def get_connection(self):
        if self.conn is None or self.cursor is None:
            return self.connect()

        return self.conn, self.cursor

    def create_table(self, table_name: str, columns: list[str]):
        conn, cursor = self.get_connection()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})")
        conn.commit()

    def list_tables(self):
        conn, cursor = self.get_connection()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [table[0] for table in  cursor.fetchall()]

    def insert(self, entity: Entity):
        conn, cursor = self.get_connection()
        columns = entity.__dataclass_fields__.keys()
        values = [getattr(entity, col) for col in columns]
        placeholders = ", ".join(["?"] * len(values))
        sql = f"INSERT INTO {entity.table_name()} ({', '.join(columns)}) VALUES ({placeholders})"
        cursor.execute(sql, values)
        conn.commit()

    def select(self, query: str) -> list[dict]:
        conn, cursor = self.get_connection()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def update(self, entity: Entity, update_values: dict):
        conn, cursor = self.get_connection()
        set_clause = ", ".join([f"{col} = ?" for col in update_values.keys()])
        sql = f"UPDATE {entity.table_name()} SET {set_clause} WHERE {entity.primary_key_column()} = ?"
        values = list(update_values.values())
        values.append(entity.primary_key)
        cursor.execute(sql, values)
        conn.commit()

    def delete(self, entity: Entity):
        conn, cursor = self.get_connection()
        sql = f"DELETE FROM {entity.table_name()} WHERE {entity.primary_key_column()} = ?"
        cursor.execute(sql, [entity.primary_key])
        conn.commit()