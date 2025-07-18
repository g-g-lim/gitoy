from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from database.entity.entity import Entity


@dataclass
class Ref(Entity):
    """
    Git reference (branch, tag, remote, etc.)
    
    Attributes:
        ref_name: Reference name like refs/heads/main, refs/tags/v1.0 (primary key)
        ref_type: Type of reference (branch, tag, remote, etc.)
        target_object_id: Target object (if direct reference)
        symbolic_target: Target ref (if symbolic reference)
        is_symbolic: True if symbolic reference
        updated_at: Last update time
        namespace: Namespace (worktree, etc.)
    """
    ref_name: str  # Primary key
    ref_type: str
    is_symbolic: bool
    head: bool
    updated_at: datetime
    target_object_id: Optional[str] = None
    symbolic_target: Optional[str] = None
    namespace: Optional[str] = None

    @property
    def is_remote(self):
        return self.ref_name.startswith("refs/remotes/")

    @property
    def branch_name(self):
        return self.ref_name.split("/")[-1]

    @property
    def primary_key(self):
        return self.ref_name

    @staticmethod
    def primary_key_column():
        return "ref_name"
    
    @staticmethod
    def table_name():
        return "ref"

    @staticmethod
    def columns():
        return [
            "ref_name TEXT PRIMARY KEY",
            "ref_type TEXT",
            "is_symbolic BOOLEAN",
            "head BOOLEAN",
            "updated_at TIMESTAMP",
            "target_object_id TEXT",
            "symbolic_target TEXT",
            "namespace TEXT",
        ]