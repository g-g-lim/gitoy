from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from database.entity.entity import Entity


@dataclass
class Blob(Entity):
    """
    Git blob object representing file content
    
    Attributes:
        object_id: SHA-1/SHA-256 hash (primary key)
        data: Raw file content
        size: File size in bytes
        encoding: File encoding (optional)
        mime_type: MIME type (optional)
        created_at: Object creation time
    """
    object_id: str  # Primary key
    data: bytes
    size: int
    created_at: datetime
    encoding: Optional[str] = None
    mime_type: Optional[str] = None 


    @staticmethod
    def table_name():
        return "blob"

    @staticmethod
    def columns():
        return [
            "object_id TEXT PRIMARY KEY",
            "data BLOB",
            "size INTEGER",
            "created_at TIMESTAMP",
            "encoding TEXT",
            "mime_type TEXT",
        ]

    