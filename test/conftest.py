"""
Pytest configuration and shared fixtures for Repository testing.
"""
import shutil
import pytest
from pathlib import Path
import sys
import tempfile

import zstandard

from src.database.sqlite import SQLite
from src.hash_algo import Sha1
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


@pytest.fixture(scope="session")
def repository_path(test_root_directory):
    repository_path = RepositoryPath(test_root_directory)
    
    yield repository_path
    
    if repository_path.repo_dir is not None:
        shutil.rmtree(repository_path.repo_dir)


@pytest.fixture(scope="function")
def sqlite(repository_path):
    sqlite = SQLite(repository_path.create_repo_db_path())

    yield sqlite

    sqlite.truncate_all()


@pytest.fixture(scope="function")  
def database(sqlite):
    database = Database(sqlite)
    return database


@pytest.fixture(scope="function")
def worktree(repository_path):
    return Worktree(repository_path)


@pytest.fixture(scope="function")
def hash_algo():
    return Sha1()


@pytest.fixture(scope="function")
def compression():
    return zstandard.ZstdCompressor()


@pytest.fixture(scope="function")
def repository(database, repository_path, worktree, compression, hash_algo):
    return Repository(
        database, repository_path, worktree, compression, hash_algo
    )


@pytest.fixture(scope="function")
def test_directory(test_root_directory):
    """
    project_root/test/test_directory
    """
    directory = test_root_directory / "test_directory"
    directory.mkdir(parents=True, exist_ok=True)

    yield directory

    # Remove all files and directories under 'directory'
    shutil.rmtree(directory)


@pytest.fixture(scope="function")
def test_file(test_directory):
    """ 
    project_root/test/test_file
    """
    # Create a temporary file
    _, path = tempfile.mkstemp(dir=test_directory)
    path = Path(path)
    path.write_text("test")

    yield path

    # Teardown: remove the file if it exists
    if path.exists():
        path.unlink()

    
@pytest.fixture(scope="function")
def test_large_file(test_directory):
    _, path = tempfile.mkstemp(dir=test_directory)
    path = Path(path)
    path.write_bytes(b"a" * 512 * 1024 * 1024)
    yield path
    if path.exists():
        path.unlink()


@pytest.fixture(scope="function")
def test_image_file(test_directory):
    image_file = test_directory / "test.png"
    image_file.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01"  # width: 1
        b"\x00\x00\x00\x01"  # height: 1
        b"\x08\x06\x00\x00\x00"  # bit depth, color type, compression, filter, interlace
        b"\x1f\x15\xc4\x89" 
        b"\x00\x00\x00\x0bIDAT"
        b"\x08\xd7c\xf8\x0f\x00\x01\x01\x01\x00\x18\xdd\x8d\x18"
        b"\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    yield image_file

    if image_file.exists():
        image_file.unlink()