from dataclasses import dataclass
from datetime import datetime

from database.entity.entity import Entity


@dataclass
class Tree(Entity):
    """
    Git tree object representing directory structure
    
    Attributes:
        object_id: SHA-1/SHA-256 hash (primary key)
        size: Tree size in bytes
        created_at: Object creation time
    """
    object_id: str  # Primary key
    size: int
    created_at: datetime 

    @staticmethod
    def table_name():
        return "tree"

    @staticmethod
    def columns():
        return [
            "object_id TEXT PRIMARY KEY",
            "size INTEGER",
            "created_at DATETIME",
        ]