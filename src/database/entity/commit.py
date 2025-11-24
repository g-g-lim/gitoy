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
        author_name: Author name
        author_email: Author email
        author_date: Author timestamp
        committer_name: Committer name
        committer_email: Committer email
        committer_date: Committer timestamp
        message: Commit message
        generation number: Commit graph depth
        created_at: Object creation time
    """

    object_id: str  # Primary key
    tree_id: str
    author_name: str
    author_email: str
    author_date: str
    committer_name: str
    committer_email: str
    committer_date: str
    message: str
    generation_number: int
    created_at: str

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
            "generation_number INTEGER",
            "created_at DATETIME",
        ]
