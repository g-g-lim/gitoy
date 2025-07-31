"""
Test suite for Repository class.

Tests all Repository methods including initialization, branch management,
error handling, and edge cases.
"""
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

from database.entity.index_entry import IndexEntry
from database.entity.blob import Blob
from database.sqlite import SQLite
from repository.repository import Repository

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


class TestRepositoryInit:
    """Test cases for Repository class."""

    def test_init_repository(self, repository: Repository):
        repository.init()
        result = repository.is_initialized()
        
        assert result is True
        assert repository.path.repo_dir is not None
        assert repository.path.get_repo_db_path() is not None


class TestRepositoryBranch:
    """Test cases for Repository branch management."""

    def test_list_branches(self, repository: Repository):
        """Test listing all branches."""
        repository.init()

        result = repository.list_branches()
        head_branch = result[0]
        
        assert head_branch.ref_name == "refs/heads/main"
        assert head_branch.head == 1
        assert head_branch.target_object_id is None
        assert head_branch.ref_type == "branch"
        assert head_branch.is_symbolic == 0
        assert head_branch.symbolic_target is None
        assert head_branch.namespace is None
        assert head_branch.updated_at is not None

    def test_create_branch_when_no_initial_commit_exists(self, repository: Repository):
        """Test creating a new branch when no initial commit exists."""
        repository.init()

        result = repository.create_branch("test_branch")
        
        assert result.success is True
        assert result.value['new'] is False

        create_ref = result.value['ref']

        assert create_ref.ref_name == "refs/heads/test_branch"
        assert create_ref.head == 1
        assert create_ref.target_object_id is None
        assert create_ref.ref_type == "branch"
        assert create_ref.is_symbolic == 0
        assert create_ref.symbolic_target is None

    def test_create_branch_with_same_name(self, repository: Repository):
        """Test creating a new branch with same name."""
        repository.init()

        result = repository.create_branch("main")
        
        assert result.success is False
        assert result.error == "Branch refs/heads/main already exists"

    # def test_create_branch_when_initial_commit_exists(self, repository):
    #     """Test creating a new branch when initial commit exists."""
    #     raise NotImplementedError()

    def test_update_head_branch(self, repository: Repository):
        """Test updating head branch."""
        repository.init()

        result = repository.update_head_branch("test_branch_1")

        assert result.success is True
        assert result.value.ref_name == "refs/heads/test_branch_1"
        assert result.value.head == 1
        assert result.value.target_object_id is None
        assert result.value.ref_type == "branch"
        assert result.value.is_symbolic == 0
        assert result.value.symbolic_target is None

    def test_update_head_branch_with_same_name(self, repository: Repository):
        """Test updating head branch with same name."""
        repository.init()

        result = repository.update_head_branch("main")

        assert result.success is False
        assert result.error == "Branch refs/heads/main already exists"
    
    # def test_delete_branch(self, repository):
    #     raise NotImplementedError()

    def test_delete_branch_when_not_exists_branch(self, repository: Repository):
        repository.init()

        result = repository.delete_branch("test_branch_2")
        assert result.success is False
        assert result.error == "Branch refs/heads/test_branch_2 not found"

    def test_delete_branch_with_head_branch(self, repository: Repository):
        repository.init()

        result = repository.delete_branch("main")
        assert result.success is False
        assert result.error == "Branch refs/heads/main is the head branch"


class TestRepositoryAddIndex:
    """Test cases for Repository add index"""

    # TODO: test for not in repository
    # def test_add_index_with_not_in_repository(self, repository: Repository):
    #     result = repository.add_index(["test_file"])
    #     assert result.success is False
    #     assert result.error == "Not in a repository"

    def test_add_index_with_not_exists_file(self, repository: Repository, test_directory: Path):
        repository.init()

        with patch('os.getcwd', return_value=test_directory.as_posix()):
            result = repository.add_index(["temp_file"])
            assert result.success is False
            assert result.error == "Path temp_file did not match any files"

    def test_add_index_with_one_file(self, sqlite: SQLite, repository: Repository, test_file_path: Path):
        repository.init()

        with patch('os.getcwd', return_value=test_file_path.parent.as_posix()):         

            result = repository.add_index([test_file_path.name])

            assert result.success is True

            hash = repository.hash(test_file_path)
            test_file_entry = repository.convert.path_to_index_entry(test_file_path)

            entry_from_db = sqlite.select(f"SELECT * FROM {IndexEntry.table_name()}")
            assert len(entry_from_db) == 1
            assert entry_from_db[0]["object_id"] == hash
            assert entry_from_db[0]["file_path"] == test_file_entry.file_path
            assert entry_from_db[0]["file_mode"] == test_file_entry.file_mode
            assert entry_from_db[0]["file_size"] == test_file_entry.file_size
            assert entry_from_db[0]["ctime"] == test_file_entry.ctime
            assert entry_from_db[0]["mtime"] == test_file_entry.mtime
            assert entry_from_db[0]["dev"] == test_file_entry.dev
            assert entry_from_db[0]["inode"] == test_file_entry.inode
            assert entry_from_db[0]["uid"] == test_file_entry.uid
            assert entry_from_db[0]["gid"] == test_file_entry.gid
            assert entry_from_db[0]["stage"] == test_file_entry.stage
            assert entry_from_db[0]["assume_valid"] == test_file_entry.assume_valid
            assert entry_from_db[0]["skip_worktree"] == test_file_entry.skip_worktree
            assert entry_from_db[0]["intent_to_add"] == test_file_entry.intent_to_add

            blobs = sqlite.select(f"SELECT * FROM {Blob.table_name()}")
            assert len(blobs) == 1
            assert blobs[0]["object_id"] == repository.hash(test_file_path)

            compressed = repository.compress(test_file_path)
            assert blobs[0]['data'] == compressed
            assert blobs[0]['size'] == test_file_path.stat().st_size

    def test_add_index_with_same_content_multiple_files(self, sqlite: SQLite, repository: Repository, test_directory: Path):
        repository.init()

        with patch('os.getcwd', return_value=test_directory.as_posix()):
            _, path1 = tempfile.mkstemp(dir=test_directory)
            _, path2 = tempfile.mkstemp(dir=test_directory)

            result = repository.add_index([Path(path1).name, Path(path2).name])
            assert result.success is True

            entries = sqlite.select(f"SELECT * FROM {IndexEntry.table_name()}")
            assert len(entries) == 2
            assert entries[0]['object_id'] == entries[1]['object_id']

            blobs = sqlite.select(f"SELECT * FROM {Blob.table_name()}")
            assert len(blobs) == 1
            assert entries[0]['object_id'] == blobs[0]['object_id']
        
    def test_add_index_with_multiple_files(self, sqlite: SQLite, repository: Repository, test_directory: Path):
        repository.init()
        
        with patch('os.getcwd', return_value=test_directory.as_posix()):
            _, path1 = tempfile.mkstemp(dir=test_directory)
            _, path2 = tempfile.mkstemp(dir=test_directory)
            Path(path2).write_bytes(b"append_data")

            result = repository.add_index([Path(path1).name, Path(path2).name])
            assert result.success is True

            entries = sqlite.select(f"SELECT * FROM {IndexEntry.table_name()}")
            assert len(entries) == 2

            blobs = sqlite.select(f"SELECT * FROM {Blob.table_name()}")
            assert len(blobs) == 2

    def test_add_index_with_mutiple_files_in_directory(self, sqlite: SQLite, repository: Repository, test_directory: Path):
        repository.init()   
    
        with patch('os.getcwd', return_value=test_directory.parent.as_posix()):
            _, path1 = tempfile.mkstemp(dir=test_directory)
            Path(path1).write_bytes(b"path1 data")
            _, path2 = tempfile.mkstemp(dir=test_directory)
            Path(path2).write_bytes(b"path2 data")

            result = repository.add_index([test_directory.name])
            assert result.success is True

            entries = sqlite.select(f"SELECT * FROM {IndexEntry.table_name()}")
            assert len(entries) == 2

            blobs = sqlite.select(f"SELECT * FROM {Blob.table_name()}")
            assert len(blobs) == 2

    def test_add_index_with_large_file(self, sqlite: SQLite, repository: Repository, test_directory: Path, test_large_file_path: Path):    
        repository.init()

        with patch('os.getcwd', return_value=test_directory.as_posix()):
            result = repository.add_index([test_large_file_path.name])
            compressed = repository.compress(test_large_file_path)

            assert result.success is True

            entries = sqlite.select(f"SELECT * FROM {IndexEntry.table_name()}")
            assert len(entries) == 1
            assert entries[0]['file_size'] == test_large_file_path.stat().st_size

            blobs = sqlite.select(f"SELECT * FROM {Blob.table_name()}")
            assert len(blobs) == 1
            assert blobs[0]["object_id"] == repository.hash(test_large_file_path)
            assert blobs[0]['data'] == compressed
            assert blobs[0]['size'] == test_large_file_path.stat().st_size
    
    def test_add_index_when_update_file_index_entry_replacement(self, sqlite: SQLite, repository: Repository, test_directory: Path):
        repository.init()
        
        with patch('os.getcwd', return_value=test_directory.as_posix()):
            _, path = tempfile.mkstemp(dir=test_directory)
            path = Path(path)
            repository.add_index([path.name])

            entries = sqlite.select(f"SELECT * FROM {IndexEntry.table_name()}")
            assert len(entries) == 1

            blobs = sqlite.select(f"SELECT * FROM {Blob.table_name()}")
            assert len(blobs) == 1
            assert entries[0]['object_id'] == blobs[0]['object_id']

            path.write_bytes(b"update data")
            result = repository.add_index([path.name])

            assert result.success is True

            entries = sqlite.select(f"SELECT * FROM {IndexEntry.table_name()}")
            assert len(entries) == 1

            blobs = sqlite.select(f"SELECT * FROM {Blob.table_name()} ORDER BY created_at ASC")
            assert len(blobs) == 2
            assert entries[0]['object_id'] == blobs[1]['object_id']
    
    def test_add_index_when_add_new_and_update_file(self, sqlite: SQLite, repository: Repository, test_directory: Path):
        repository.init()
        
        with patch('os.getcwd', return_value=test_directory.as_posix()):
            _, path = tempfile.mkstemp(dir=test_directory)
            path = Path(path)
            repository.add_index([path.name])

            path.write_bytes(b"update file")
            _, path2 = tempfile.mkstemp(dir=test_directory)
            path2 = Path(path2)
            path2.write_bytes(b"new file")
            result = repository.add_index([path.name, path2.name])

            assert result.success is True

            entries = sqlite.select(f"SELECT * FROM {IndexEntry.table_name()}")
            assert len(entries) == 2

            blobs = sqlite.select(f"SELECT * FROM {Blob.table_name()}")
            assert len(blobs) == 3

    def test_add_index_when_add_completed_same_file(self, sqlite: SQLite, repository: Repository, test_directory: Path):
        repository.init()
        
        with patch('os.getcwd', return_value=test_directory.as_posix()):
            _, path = tempfile.mkstemp(dir=test_directory)
            path = Path(path)

            repository.add_index([path.name])
            repository.add_index([path.name])

            entries = sqlite.select(f"SELECT * FROM {IndexEntry.table_name()}")
            assert len(entries) == 1

            blobs = sqlite.select(f"SELECT * FROM {Blob.table_name()}")
            assert len(blobs) == 1

    def test_add_index_duplicate_paths_in_single_call(self, sqlite: SQLite, repository: Repository, test_directory: Path):
        repository.init()
        
        with patch('os.getcwd', return_value=test_directory.as_posix()):
            _, path = tempfile.mkstemp(dir=test_directory)
            path = Path(path)

            repository.add_index([path.name, path.name])

            entries = sqlite.select(f"SELECT * FROM {IndexEntry.table_name()}")
            assert len(entries) == 1

            blobs = sqlite.select(f"SELECT * FROM {Blob.table_name()}")
            assert len(blobs) == 1