from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from database.entity.entity import Entity


@dataclass
class Commit(Entity):
    """
    Git commit object
    
    Attributes:
        object_id: SHA-1/SHA-256 hash (primary key)
        tree_id: Root tree object_id
        author_name: Author name
        author_email: Author email
        author_date: Author timestamp
        committer_name: Committer name
        committer_email: Committer email
        committer_date: Committer timestamp
        message: Commit message
        size: Commit size in bytes
        created_at: Object creation time
        encoding: Message encoding (optional)
    """
    object_id: str  # Primary key
    tree_id: str
    author_name: str
    author_email: str
    author_date: datetime
    committer_name: str
    committer_email: str
    committer_date: datetime
    message: str
    size: int
    created_at: datetime
    encoding: Optional[str] = None 

    @staticmethod
    def table_name():
        return "commits"

    @staticmethod
    def columns():
        return [
            "object_id TEXT PRIMARY KEY",
            "tree_id TEXT",
            "author_name TEXT",
            "author_email TEXT",
            "author_date DATETIME",
            "committer_name TEXT",
            "committer_email TEXT",
            "committer_date DATETIME",
            "message TEXT",
            "size INTEGER",
            "created_at DATETIME",
            "encoding TEXT",
        ]