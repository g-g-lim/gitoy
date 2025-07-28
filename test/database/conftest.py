from src.database.database import Database
from src.database.sqlite import SQLite
import pytest


@pytest.fixture(scope="function")
def sqlite_db_path(test_directory):
    db_path = test_directory / "test.db"
    yield db_path


@pytest.fixture(scope="function")
def sqlite(sqlite_db_path):
    sqlite = SQLite(sqlite_db_path)

    yield sqlite

    if sqlite.path is not None and sqlite.path.exists():
        sqlite.truncate_all()


@pytest.fixture(scope="function")  
def database(sqlite):
    database = Database(sqlite)
    database.init()
    return database