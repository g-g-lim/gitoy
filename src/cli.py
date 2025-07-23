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
from hash_algo import Sha1
from worktree import Worktree
from repository_path import RepositoryPath
from util.console import Console
from command import Command
import zstandard

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
    
    def __init__(self, command_list: list[Command]):
        """Initialize Gitoy CLI"""

        for command in command_list:
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
    repository_path = RepositoryPath()
    repo_db_path = None
    if repository_path.repo_dir is None:
        repo_db_path = repository_path.create_repo_db_path()
    else:
        repo_db_path = repository_path.get_repo_db_path()

    sqlite = SQLite(repo_db_path)
    database = Database(sqlite)
    worktree = Worktree(repository_path)
    compressor = zstandard.ZstdCompressor()
    hash_algo = Sha1()
    repository = Repository(database, repository_path, worktree, compressor, hash_algo)
    console = Console()
    command_list = [
        Init(repository, console), 
        Branch(repository, console),
        Add(repository, console)
    ]

    app = GitoyCLI(command_list)
    fire.Fire(app)

if __name__ == "__main__":
    main() 