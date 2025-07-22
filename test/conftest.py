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
def test_root_directory():
    """
    The root directory of the test suite.
    project_root/test/
    """
    return Path(__file__).parent


@pytest.fixture(scope="function")
def temp_directory(test_root_directory):
    """
    project_root/test/test_directory
    """
    directory = test_root_directory / "test_directory"
    directory.mkdir(parents=True, exist_ok=True)

    yield directory

    # Remove all files and directories under 'directory'
    shutil.rmtree(directory)


@pytest.fixture(scope="function")
def temp_file(test_root_directory):
    """ 
    project_root/test/test_file
    """
    # Create a temporary file
    _, path = tempfile.mkstemp(dir=test_root_directory)
    path = Path(path)
    path.write_text("test")

    yield path

    # Teardown: remove the file if it exists
    if path.exists():
        path.unlink()


@pytest.fixture(scope="session")
def repository_path(test_root_directory):
    repository_path = RepositoryPath(test_root_directory)
    
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
