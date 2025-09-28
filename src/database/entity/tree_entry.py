from dataclasses import dataclass
from typing import Optional

from database.entity.entity import Entity


@dataclass
class TreeEntry(Entity):
    """
    Entry within a Git tree object

    Attributes:
        tree_id: Parent tree object_id (part of composite primary key)
        entry_name: File/directory name (part of composite primary key)
        entry_mode: File permissions (octal)
        entry_object_id: Referenced object_id
        entry_type: Type of referenced object (blob, tree, commit for submodules)
    """

    entry_name: str
    entry_mode: str
    entry_type: str  # "blob", "tree", "commit"
    entry_object_id: Optional[str]
    tree_id: Optional[str] = None

    def __post_init__(self):
        self.parent: Optional[TreeEntry] = None
        self.children: list[TreeEntry] = []
        self.relative_path: Optional[str] = None

    @staticmethod
    def table_name():
        return "tree_entry"

    @staticmethod
    def columns():
        return [
            "tree_id TEXT",
            "entry_name TEXT",
            "entry_mode TEXT",
            "entry_object_id TEXT",
            "entry_type TEXT",
        ]

    @property
    def hashable_str(self):
        return f"{self.entry_mode}:{self.entry_type}:{self.entry_object_id}:{self.entry_name}"

    def append_child(self, tree_entry: "TreeEntry"):
        self.children.append(tree_entry)
        tree_entry.parent = self

    def remove_child(self, tree_entry: "TreeEntry"):
        self.children.remove(tree_entry)
        tree_entry.parent = None
