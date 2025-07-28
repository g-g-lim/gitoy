# Add src to path
from pathlib import Path
import random
import sys
import time

from src.database.entity.index_entry import IndexEntry
from src.database.database import Database


src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

class TestDatabase:
    """Test cases for Database class."""

    def random_index_entry(self, file_path = None) -> IndexEntry:
        """Create a random IndexEntry fixture for testing."""
        if file_path is None:
            file_path = f"test/file{random.randint(1, 1000)}.txt"
        
        return IndexEntry(
            file_path=file_path,
            object_id=f"{random.randint(1000000000, 9999999999):010d}{random.randint(1000000000, 9999999999):010d}",
            file_mode=random.choice(["100644", "100755", "120000"]),
            file_size=random.randint(0, 10000),
            ctime=time.time() - random.randint(0, 86400),
            mtime=time.time() - random.randint(0, 86400),
            dev=random.randint(1, 100),
            inode=random.randint(1000, 999999),
            uid=random.randint(500, 1000),
            gid=random.randint(20, 100),
            stage=random.randint(0, 3),
            assume_valid=random.choice([True, False]),
            skip_worktree=random.choice([True, False]),
            intent_to_add=random.choice([True, False])
        )

    def test_list_index_entries_by_paths_startwith(self, database: Database):
        database.create_index_entries(
            [
                self.random_index_entry('./file.txt'),
                self.random_index_entry('./test/file1.txt'),
                self.random_index_entry('./test/test2/file2.txt'),
                self.random_index_entry('./test/test2/test3/file3.txt'),
                self.random_index_entry('./test/test2/test3/file4.txt'),
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
