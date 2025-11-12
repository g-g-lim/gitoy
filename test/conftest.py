"""
Pytest configuration and shared fixtures for testing.
"""

import shutil
import pytest
from pathlib import Path
import sys
import tempfile

from src.repository.commit_store import CommitStore
from src.repository.compress_file import CompressFile
from src.repository.convert import Convert
from src.repository.hash_file import HashFile
from src.repository.path_validator import PathValidator
import zstandard

from src.repository.blob_store import BlobStore
from src.repository.index_store import IndexStore
from src.repository.tree_store import TreeStore
from src.database.sqlite import SQLite
from src.repository.worktree import Worktree
from src.repository.repo_path import RepositoryPath
from src.database.database import Database
from src.repository.repository import Repository

root_path = Path(__file__).parent.parent
src_path = root_path / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


TEST_GITOY_DIR = ".gitoy_test"


@pytest.fixture(scope="function")
def test_repo_directory():
    """
    project_root/test/test_repo
    """
    repo_dir_path = root_path / "test" / "test_repo"
    repo_dir_path.mkdir(parents=True, exist_ok=True)

    yield repo_dir_path

    shutil.rmtree(repo_dir_path)


@pytest.fixture(scope="function")
def repository_path(test_repo_directory):
    repository_path = RepositoryPath(test_repo_directory, TEST_GITOY_DIR)

    yield repository_path

    if repository_path.repo_dir is not None:
        shutil.rmtree(repository_path.repo_dir)


@pytest.fixture(scope="function")
def sqlite(repository_path):
    sqlite = SQLite(repository_path.create_repo_db_path())

    yield sqlite

    if sqlite.path is not None and sqlite.path.exists():
        sqlite.truncate_all()


@pytest.fixture(scope="function")
def database(sqlite):
    database = Database(sqlite)
    return database


@pytest.fixture(scope="function")
def worktree(repository_path):
    return Worktree(repository_path)


@pytest.fixture(scope="function")
def hash_file():
    return HashFile()


@pytest.fixture(scope="function")
def compress_file():
    return CompressFile(zstandard.ZstdCompressor(), zstandard.ZstdDecompressor())


@pytest.fixture(scope="function")
def index_store(database, repository_path):
    return IndexStore(database, repository_path)


@pytest.fixture(scope="function")
def convert(hash_file, compress_file, repository_path):
    return Convert(hash_file, compress_file, repository_path)


@pytest.fixture(scope="function")
def path_validator(worktree, index_store):
    return PathValidator(worktree, index_store)


@pytest.fixture(scope="function")
def blob_store(database):
    return BlobStore(database)


@pytest.fixture(scope="function")
def tree_store(database):
    return TreeStore(database)


@pytest.fixture(scope="function")
def commit_store(database: Database):
    return CommitStore(database)


@pytest.fixture(scope="function")
def repository(
    database,
    repository_path,
    worktree,
    compress_file,
    hash_file,
    index_store,
    blob_store,
    convert,
    path_validator,
    tree_store,
    commit_store,
):
    return Repository(
        database,
        repository_path,
        worktree,
        compress_file,
        hash_file,
        index_store,
        blob_store,
        convert,
        path_validator,
        tree_store,
        commit_store,
    )


@pytest.fixture(scope="function")
def test_directory(test_repo_directory):
    """
    project_root/test/test_repo/test_dir
    """
    directory = test_repo_directory / "test_dir"
    directory.mkdir(parents=True, exist_ok=True)

    yield directory

    # Remove all files and directories under 'directory'
    if directory.exists():
        shutil.rmtree(directory)


@pytest.fixture(scope="function")
def test_file_path(test_directory):
    """
    project_root/test/test_repo/test_dir/test_file
    """
    _, path = tempfile.mkstemp(dir=test_directory)
    path = Path(path)

    yield path

    if path.exists():
        path.unlink()


@pytest.fixture(scope="function")
def test_large_file_path(test_directory):
    """
    project_root/test/test_repo/test_dir/test_large_file
    """
    _, path = tempfile.mkstemp(dir=test_directory)
    path = Path(path)
    path.write_bytes(b"a" * 512 * 1024 * 1024)

    yield path

    if path.exists():
        path.unlink()


@pytest.fixture(scope="function")
def test_image_file_path(test_directory):
    """
    project_root/test/test_repo/test_dir/test_image_file
    """
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
