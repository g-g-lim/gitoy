"""
Common type definitions for the gitoy project.
"""

from typing import Union, TypedDict
from pathlib import Path

# Type alias for readable buffer types that can be used with hash functions
ReadableBuffer = Union[bytes, bytearray, memoryview]


class StatusData(TypedDict):
    branch_name: str
    unstaged: dict[str, list[Path]]
    staged: dict[str, list[Path]]
    untracked: list[Path]
