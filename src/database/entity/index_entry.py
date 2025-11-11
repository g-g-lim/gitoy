from dataclasses import dataclass
from pathlib import Path
from typing import Optional


from database.entity.entity import Entity


@dataclass
class IndexEntry(Entity):
    """
    Git index entry representing staged file

    Attributes:
        path: Relative file path (primary key)
        object_id: Staged object_id
        mode: File permissions
        size: File size in bytes
    """

    path: str  # Primary key
    object_id: str
    mode: str
    size: Optional[int] = None

    @staticmethod
    def primary_key_column():
        return "path"

    @staticmethod
    def table_name():
        return "index_entry"

    @staticmethod
    def columns():
        return [
            "path TEXT PRIMARY KEY",
            "object_id TEXT",
            "mode TEXT",
            "size INTEGER",
        ]

    def __eq__(self, other: "IndexEntry"):
        return (
            self.path == other.path
            and self.object_id == other.object_id
            and self.mode == other.mode
            and self.size == other.size
        )

    @property
    def file_path_obj(self):
        return Path(self.path)

    def absolute_path(self, root_path: Path):
        return root_path / self.file_path_obj

    def relative_path(self, root_path: Path):
        return self.absolute_path(root_path).relative_to(root_path)

    @property
    def file_name(self):
        return self.file_path_obj.name
