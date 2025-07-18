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
from util.file_handler import FileHandler
from util.console import Console


class GitoyCLI:
    """
    🚀 Gitoy CLI

    A simple File Version Control CLI tool built with Python Fire
    
    Commands:
    - version: Show version information
    - init: Initialize a new Gitoy repository
    - add: Add a file to the Gitoy repository index
    - branch: List, create, or delete branches
    """
    
    def __init__(self, commands = []):
        """Initialize Gitoy CLI"""
        for command in commands:
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
    file_handler = FileHandler()
    
    sqlite = SQLite(file_handler)
    database = Database(sqlite)
    
    repository = Repository(database, file_handler)
    console = Console()
    command_list = [Init(repository, console), Branch(repository, console)]

    fire.Fire(GitoyCLI(command_list))

if __name__ == "__main__":
    main() 