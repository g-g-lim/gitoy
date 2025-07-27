import sqlite3
from pathlib import Path
from typing import Optional

from database.entity.entity import Entity


class SQLite:

    def __init__(self, path: Path | None = None):
        self.path = path    
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None

    def connect(self):
        if self.path is None:
            raise ValueError("Path is not set")
        
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
    
    def truncate_table(self, table_name: str):
        conn, cursor = self.get_connection()
        cursor.execute(f"DELETE FROM {table_name}")
        conn.commit()

    def truncate_all(self):
        tables = self.list_tables()
        for table in tables:
            self.truncate_table(table)

    def insert(self, entity: Entity):
        conn, cursor = self.get_connection()
        columns = entity.__dataclass_fields__.keys()
        values = [getattr(entity, col) for col in columns]
        placeholders = ", ".join(["?"] * len(values))
        sql = f"INSERT INTO {entity.table_name()} ({', '.join(columns)}) VALUES ({placeholders})"
        cursor.execute(sql, values)
        conn.commit()

    def insert_many(self, entities: list[Entity]):
        if not entities:
            return []
            
        conn, cursor = self.get_connection()
        
        # Use the first entity to get table and column information
        first_entity = entities[0]
        table_name = first_entity.table_name()
        columns = list(first_entity.__dataclass_fields__.keys())
        placeholders = ", ".join(["?"] * len(columns))
        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        
        # Prepare values for all entities
        values_list = [
            [getattr(entity, col) for col in columns]
            for entity in entities
        ]
        
        cursor.executemany(sql, values_list)
        conn.commit()

        return entities

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

    def delete_many(self, entities: list[Entity]):
        entities = [entity.primary_key for entity in entities]
        conn, cursor = self.get_connection()
        sql = f"DELETE FROM {entities[0].table_name()} WHERE {entities[0].primary_key_column()} IN ({', '.join(['?'] * len(entities))})"
        cursor.execute(sql, [entity.primary_key for entity in entities])
        conn.commit()