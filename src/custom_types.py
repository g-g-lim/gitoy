"""
Common type definitions for the gitoy project.
"""
from typing import Union

# Type alias for readable buffer types that can be used with hash functions
ReadableBuffer = Union[bytes, bytearray, memoryview] 