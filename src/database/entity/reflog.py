from dataclasses import dataclass
from datetime import datetime

from database.entity.entity import Entity


@dataclass
class Reflog(Entity):
    """
    Git reflog entry tracking reference changes
    
    Attributes:
        ref_name: Reference name (part of composite primary key)
        timestamp: When change occurred (part of composite primary key)
        old_object_id: Previous object_id
        new_object_id: New object_id
        committer_name: Who made the change
        committer_email: Committer email
        message: Reflog message
        sequence: Sequence number
    """
    ref_name: str  # Primary key component
    timestamp: datetime  # Primary key component
    old_object_id: str
    new_object_id: str
    committer_name: str
    committer_email: str
    message: str
    sequence: int 

    @staticmethod
    def table_name():
        return "reflog"

    @staticmethod
    def columns():
        return [
            "ref_name TEXT",
            "timestamp DATETIME",
            "old_object_id TEXT",
            "new_object_id TEXT",
            "committer_name TEXT",
            "committer_email TEXT",
            "message TEXT",
            "sequence INTEGER",
        ]