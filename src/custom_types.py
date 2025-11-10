"""
Common type definitions for the gitoy project.
"""

from dataclasses import dataclass
from typing import Optional, Union

from database.entity.index_entry import IndexEntry

# Type alias for readable buffer types that can be used with hash functions
ReadableBuffer = Union[bytes, bytearray, memoryview]

@dataclass
class Changes:
    added: list[IndexEntry]
    modified: list[IndexEntry]
    deleted: list[IndexEntry]

@dataclass
class StatusResult:
    branch_name: str
    unstaged: Optional[Changes] = None
    staged: Optional[Changes] = None
