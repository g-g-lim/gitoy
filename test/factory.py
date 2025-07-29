import random
import time
from database.entity.index_entry import IndexEntry


def random_index_entry(file_path = None) -> IndexEntry:
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