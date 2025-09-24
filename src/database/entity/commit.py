from dataclasses import dataclass
from datetime import datetime

from database.entity.entity import Entity


@dataclass
class Commit(Entity):
    """
    Git commit object

    Attributes:
        object_id: SHA-1/SHA-256 hash (primary key)
        tree_id: Root tree object_id
        committer_name: Committer name
        committer_email: Committer email
        committer_date: Committer timestamp
        message: Commit message
        created_at: Object creation time
    """

    object_id: str  # Primary key
    tree_id: str
    committer_name: str
    committer_email: str
    committer_date: datetime
    message: str
    created_at: datetime

    @staticmethod
    def table_name():
        return "commits"

    @staticmethod
    def columns():
        return [
            "object_id TEXT PRIMARY KEY",
            "tree_id TEXT",
            "committer_name TEXT",
            "committer_email TEXT",
            "committer_date DATETIME",
            "message TEXT",
            "created_at DATETIME",
        ]
