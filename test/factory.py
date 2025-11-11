import random
import time

from src.database.entity.index_entry import IndexEntry


def random_index_entry(file_path=None) -> IndexEntry:
    """Create a random IndexEntry fixture for testing."""
    if file_path is None:
        file_path = f"test/file{random.randint(1, 1000)}.txt"

    return IndexEntry(
        path=file_path,
        object_id=f"{random.randint(1000000000, 9999999999):010d}{random.randint(1000000000, 9999999999):010d}",
        mode=random.choice(["100644", "100755", "120000"]),
        size=random.randint(0, 10000),
    )
