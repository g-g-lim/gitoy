"""
Pytest configuration and shared fixtures for Repository testing.
"""
import pytest
from datetime import datetime
from pathlib import Path
import sys

from database.sqlite import SQLite
from database.entity.ref import Ref
from util.file_handler import FileHandler
from database.database import Database
from repository import Repository


src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session")
def file_handler():
    file_handler = FileHandler()    
    
    yield file_handler

    # teardown
    for item in file_handler.repo_dir.iterdir():
        if item.is_file():
           item.unlink()
    file_handler.repo_dir.rmdir()


@pytest.fixture(scope="session")
def sqlite(file_handler):
    return SQLite(file_handler)


@pytest.fixture(scope="session")  
def database(sqlite):
    database = Database(sqlite)
    return database


@pytest.fixture(scope="session")
def repository(database, file_handler):
    return Repository(database, file_handler)


@pytest.fixture
def main_ref_instance   () -> Ref:
    """Factory function to create test Ref entities."""
    return Ref(
        ref_name="refs/heads/main",
        ref_type="branch", 
        is_symbolic=False,
        head=True,
        updated_at=datetime.now(),
        target_object_id=None,
        symbolic_target=None,
        namespace=None
    )