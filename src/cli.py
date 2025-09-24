#!/usr/bin/env python3
"""
Gitoy CLI - A simple File Version Control CLI tool built with Python Fire
"""

import fire
import sys

from repository.blob_store import BlobStore
from repository.compress_file import CompressFile
from repository.convert import Convert
from repository.hash_file import HashFile
from repository.index_diff import IndexDiff
from repository.index_store import IndexStore
from repository.path_validator import PathValidator
from repository.repository import Repository
from command.init import Init
from database.database import Database
from database.sqlite import SQLite
from command.branch import Branch
from command.add import Add
from command.status import Status
from repository.tree_diff import TreeDiff
from repository.tree_store import TreeStore
from repository.worktree import Worktree
from repository.repo_path import RepositoryPath
from util.console import Console
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
    - status: Show the working tree status
    """

    def __init__(self, commands):
        """Initialize Gitoy CLI"""

        for command in commands:
            setattr(self, command.__class__.__name__.lower(), command)

    def version(self):
        """Show version information"""
        return {
            "name": "Gitoy CLI",
            "version": "0.1.0",
            "description": "A simple File Version Control CLI tool built with Python",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
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
    compress_file = CompressFile(zstandard.ZstdCompressor())
    index_store = IndexStore(database, repository_path)
    blob_store = BlobStore(database)
    hash_file = HashFile()
    convert = Convert(hash_file, compress_file, repository_path)
    index_diff = IndexDiff(index_store, worktree, convert)
    path_validator = PathValidator(worktree, index_store)
    tree_store = TreeStore(database)
    tree_diff = TreeDiff(index_store, tree_store)
    repository = Repository(
        database,
        repository_path,
        worktree,
        compress_file,
        hash_file,
        index_store,
        blob_store,
        convert,
        index_diff,
        path_validator,
        tree_store,
        tree_diff,
    )
    console = Console()
    commands = [
        Init(repository, console),
        Branch(repository, console),
        Add(repository, console),
        Status(repository, console),
    ]
    app = GitoyCLI(commands)
    fire.Fire(app)


if __name__ == "__main__":
    main()
