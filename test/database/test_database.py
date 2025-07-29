# Add src to path
from pathlib import Path
import sys

from src.database.database import Database
from test.factory import random_index_entry


src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

class TestDatabase:
    """Test cases for Database class."""

    def test_list_index_entries_by_paths_startwith(self, database: Database):
        database.create_index_entries(
            [
                random_index_entry('./file.txt'),
                random_index_entry('./test/file1.txt'),
                random_index_entry('./test/test2/file2.txt'),
                random_index_entry('./test/test2/test3/file3.txt'),
                random_index_entry('./test/test2/test3/file4.txt'),
            ]
        )

        entries = database.list_index_entries()
        assert len(entries) == 5

        entries = database.list_index_entries_by_paths_startwith(['./'])
        assert len(entries) == 5

        entries = database.list_index_entries_by_paths_startwith(['./test/file1.txt', './test/test2/file2.txt'])
        assert len(entries) == 2

        entries = database.list_index_entries_by_paths_startwith(['./test'])
        assert len(entries) == 4

        entries = database.list_index_entries_by_paths_startwith(['./test/test2'])
        assert len(entries) == 3

        entries = database.list_index_entries_by_paths_startwith(['test2'])
        assert len(entries) == 0

        entries = database.list_index_entries_by_paths_startwith(['./test/test2/test3'])
        assert len(entries) == 2

        entries = database.list_index_entries_by_paths_startwith(['./test/test2/test3', './test'])
        assert len(entries) == 4
