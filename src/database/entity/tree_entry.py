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

    tree_id: str  # Primary key component
    entry_name: str  # Primary key component
    entry_mode: str
    entry_object_id: str
    entry_type: str  # "blob", "tree", "commit"

    def __post_init__(self):
        self.parent: Optional[TreeEntry] = None
        self.children: list[TreeEntry] = []

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

    def append_child(self, tree_entry: "TreeEntry"):
        self.children.append(tree_entry)
        tree_entry.parent = self

    def remove_child(self, tree_entry: "TreeEntry"):
        self.children.remove(tree_entry)
        tree_entry.parent = None
