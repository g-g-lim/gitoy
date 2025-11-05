from dataclasses import dataclass
from datetime import datetime

from database.entity.entity import Entity


@dataclass
class Tag(Entity):
    """
    Git tag object

    Attributes:
        object_id: SHA-1/SHA-256 hash (primary key)
        tag_name: Tag name
        tagged_object_id: Referenced object_id
        tagged_type: Type of tagged object (blob, tree, commit)
        tagger_name: Tagger name
        tagger_email: Tagger email
        tagger_date: Tag timestamp
        message: Tag message
        size: Tag size in bytes
        created_at: Object creation time
    """

    object_id: str  # Primary key
    tag_name: str
    tagged_object_id: str
    tagged_type: str  # "blob", "tree", "commit"
    tagger_name: str
    tagger_email: str
    tagger_date: datetime
    message: str
    size: int
    created_at: datetime

    @staticmethod
    def table_name():
        return "tag"

    @staticmethod
    def columns():
        return [
            "object_id TEXT PRIMARY KEY",
            "tag_name TEXT",
            "tagged_object_id TEXT",
            "tagged_type TEXT",
            "tagger_name TEXT",
            "tagger_email TEXT",
            "tagger_date DATETIME",
            "message TEXT",
            "size INTEGER",
            "created_at DATETIME",
        ]
