#!/usr/bin/env python3
"""
Gitoy CLI - A simple File Version Control CLI tool built with Python Fire
"""

import fire
import sys

from repository import Repository
from command.init import Init
from database.database import Database
from database.sqlite import SQLite
from command.branch import Branch
from command.add import Add
from worktree import Worktree
from util.repository_file import RepositoryFile
from util.console import Console


class GitoyCLI:
    """
    🚀 Gitoy CLI

    A simple File Version Control CLI tool built with Python Fire
    
    Commands:
    - version: Show version information
    - init: Initialize a new Gitoy repository
    - branch: List, create, or delete branches
    - add: Add a file to the Gitoy repository index
    """
    
    def __init__(self):
        """Initialize Gitoy CLI"""

        _repository_file = RepositoryFile()
        _sqlite = SQLite(_repository_file.create_repo_db_path())
        _database = Database(_sqlite)
        _worktree = Worktree(_repository_file)
        _repository = Repository(_database, _repository_file, _worktree)
        _console = Console()
        _command_list = [
            Init(_repository, _console), 
            Branch(_repository, _console),
            Add(_repository, _console)
        ]

        for command in _command_list:
            setattr(self, command.__class__.__name__.lower(), command)
    
    def version(self):
        """Show version information"""
        return {
            "name": "Gitoy CLI",
            "version": "0.1.0",
            "description": "A simple File Version Control CLI tool built with Python",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        }

def main():
    """Main entry point for Gitoy CLI"""
    app = GitoyCLI()
    fire.Fire(app)

if __name__ == "__main__":
    main() 