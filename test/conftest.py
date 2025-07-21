"""
Pytest configuration and shared fixtures for Repository testing.
"""
import pytest
from pathlib import Path
import sys

from database.sqlite import SQLite
from util.repository_file import RepositoryFile
from database.database import Database
from repository import Repository


src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session")
def repository_file():
    repository_file = RepositoryFile() 
    
    yield repository_file

    # teardown
    for item in repository_file.repo_dir_path.iterdir():
        if item.is_file():
           item.unlink()
    repository_file.repo_dir_path.rmdir()


@pytest.fixture(scope="session")
def sqlite(repository_file):
    return SQLite(repository_file.create_repo_db_path())


@pytest.fixture(scope="session")  
def database(sqlite):
    database = Database(sqlite)
    return database


@pytest.fixture(scope="session")
def repository(database, repository_file):
    return Repository(database, repository_file)