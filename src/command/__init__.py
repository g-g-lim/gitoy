from typing import Protocol, Any

# Re-export command classes for easier imports
from .add import Add
from .branch import Branch  
from .init import Init
from .status import Status

class Command(Protocol):
    """Command interface that all gitoy commands should implement"""
    
    def __init__(self, **kwargs: Any):
        """Initialize command with repository and console"""
        ...
    
    def __call__(self, *args: str):
        """Execute the command with given arguments"""
        ...


__all__ = [Command, Add, Branch, Init, Status] 