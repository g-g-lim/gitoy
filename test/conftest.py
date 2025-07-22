"""
Pytest configuration and shared fixtures for Repository testing.
"""
import shutil
import pytest
from pathlib import Path
import sys
import tempfile

from src.database.sqlite import SQLite
from src.worktree import Worktree
from src.repository_path import RepositoryPath
from src.database.database import Database
from src.repository import Repository


src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session")
def repository_path():
    test_directory = Path(__file__).parent
    repository_path = RepositoryPath(test_directory)
    
    yield repository_path
    
    if repository_path.repo_dir is not None:
        shutil.rmtree(repository_path.repo_dir)


@pytest.fixture(scope="session")
def sqlite(repository_path):
    return SQLite(repository_path.create_repo_db_path())


@pytest.fixture(scope="session")  
def database(sqlite):
    database = Database(sqlite)
    return database


@pytest.fixture(scope="session")
def worktree(repository_path):
    return Worktree(repository_path)


@pytest.fixture(scope="session")
def repository(database, repository_path, worktree):
    return Repository(database, repository_path, worktree)


@pytest.fixture(scope="function")
def temp_directory(repository_path):
    directory = repository_path.repo_dir.parent / "test_directory"
    directory.mkdir(parents=True, exist_ok=True)

    yield directory

    # Remove all files and directories under 'directory'
    shutil.rmtree(directory)


@pytest.fixture(scope="function")
def temp_file(repository_path):
    # Create a temporary file
    fd, path = tempfile.mkstemp(dir=repository_path.repo_dir.parent)
    path = Path(path)
    path.write_text("test")

    yield path.name

    # Teardown: remove the file if it exists
    if path.exists():
        path.unlink()
