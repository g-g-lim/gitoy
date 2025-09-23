from dataclasses import dataclass
from pathlib import Path
from typing import Optional


from database.entity.entity import Entity


@dataclass
class IndexEntry(Entity):
    """
    Git index entry representing staged file

    Attributes:
        file_path: Relative file path (primary key)
        object_id: Staged object_id
        file_mode: File permissions
        file_size: File size in bytes
        ctime: Change time
        mtime: Modification time
        dev: Device ID
        inode: Inode number
        uid: User ID
        gid: Group ID
        stage: Merge stage (0-3)
        assume_valid: Assume valid flag
        skip_worktree: Skip worktree flag
        intent_to_add: Intent to add flag
    """

    file_path: str  # Primary key
    object_id: str
    file_mode: str
    file_size: Optional[int] = None
    ctime: Optional[int | float] = None
    mtime: Optional[int | float] = None
    dev: Optional[int] = None
    inode: Optional[int] = None
    uid: Optional[int] = None
    gid: Optional[int] = None
    stage: Optional[int] = None
    assume_valid: Optional[bool] = None
    skip_worktree: Optional[bool] = None
    intent_to_add: Optional[bool] = None

    @staticmethod
    def primary_key_column():
        return "file_path"

    @staticmethod
    def table_name():
        return "index_entry"

    @staticmethod
    def columns():
        return [
            "file_path TEXT PRIMARY KEY",
            "object_id TEXT",
            "file_mode TEXT",
            "file_size INTEGER",
            "ctime INTEGER",
            "mtime INTEGER",
            "dev INTEGER",
            "inode INTEGER",
            "uid INTEGER",
            "gid INTEGER",
            "stage INTEGER",
            "assume_valid BOOLEAN",
            "skip_worktree BOOLEAN",
            "intent_to_add BOOLEAN",
        ]

    def __eq__(self, other: "IndexEntry"):
        return (
            self.file_path == other.file_path
            and self.object_id == other.object_id
            and self.file_size == other.file_size
            and self.file_mode == other.file_mode
            and self.mtime == other.mtime
        )

    @property
    def file_path_obj(self):
        return Path(self.file_path)

    def absolute_path(self, root_path: Path):
        return root_path / self.file_path_obj

    @property
    def file_name(self):
        return self.file_path_obj.name
