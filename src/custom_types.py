"""
Common type definitions for the gitoy project.
"""

from dataclasses import dataclass
from typing import Union

from database.entity.index_entry import IndexEntry

# Type alias for readable buffer types that can be used with hash functions
ReadableBuffer = Union[bytes, bytearray, memoryview]


@dataclass
class Diff:
    added: list[IndexEntry]
    modified: list[IndexEntry]
    deleted: list[IndexEntry]

    def is_empty(self) -> bool:
        return not (self.added or self.modified or self.deleted)
    
    def all(self) -> list[IndexEntry]:
        return self.added + self.modified + self.deleted


@dataclass
class StatusResult:
    branch_name: str
    unstaged: Diff
    staged: Diff

    def __init__(self, branch_name: str) -> None:
        self.branch_name = branch_name
        self.unstaged = Diff([], [], [])
        self.staged = Diff([], [], [])
