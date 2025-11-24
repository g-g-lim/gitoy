"""
Test suite for Repository class.

Tests all Repository methods including initialization, branch management,
error handling, and edge cases.
"""

import datetime
from pathlib import Path
import sys
import tempfile
from unittest import mock
from unittest.mock import patch

from src.database.database import Database
from src.database.entity.commit import Commit
from src.database.entity.index_entry import IndexEntry
from src.database.entity.blob import Blob
from src.database.entity.tree_entry import TreeEntry
from src.database.sqlite import SQLite
from src.repository.convert import Convert
from src.repository.repo_path import RepositoryPath
from src.repository.repository import Repository
from src.repository.tree_store import TreeStore

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
        assert result.value["new"] is False

        create_ref = result.value["ref"]

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

        result = repository.update_head_branch_name("test_branch_1")

        assert result.success is True
        assert result.value is not None
        assert result.value.ref_name == "refs/heads/test_branch_1"
        assert result.value.head == 1
        assert result.value.target_object_id is None
        assert result.value.ref_type == "branch"
        assert result.value.is_symbolic == 0
        assert result.value.symbolic_target is None

    def test_update_head_branch_with_same_name(self, repository: Repository):
        """Test updating head branch with same name."""
        repository.init()

        result = repository.update_head_branch_name("main")

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

    def test_add_index_with_not_exists_file(
        self, repository: Repository, test_directory: Path
    ):
        repository.init()

        with patch("os.getcwd", return_value=test_directory.as_posix()):
            result = repository.add_index(["temp_file"])
            assert result.success is False
            assert result.error == "Path temp_file did not match any files"

    def test_add_index_with_one_file(
        self, sqlite: SQLite, repository: Repository, test_file_path: Path
    ):
        repository.init()

        with patch("os.getcwd", return_value=test_file_path.parent.as_posix()):
            result = repository.add_index([test_file_path.name])

            assert result.success is True

            hash = repository.hash_file.hash(test_file_path)
            test_file_entry = repository.convert.path_to_index_entry(test_file_path)

            entry_from_db = sqlite.select(f"SELECT * FROM {IndexEntry.table_name()}")
            assert len(entry_from_db) == 1
            assert entry_from_db[0]["object_id"] == hash
            assert entry_from_db[0]["path"] == test_file_entry.path
            assert entry_from_db[0]["mode"] == test_file_entry.mode
            assert entry_from_db[0]["size"] == test_file_entry.size

            blobs = sqlite.select(f"SELECT * FROM {Blob.table_name()}")
            assert len(blobs) == 1
            assert blobs[0]["object_id"] == repository.hash_file.hash(test_file_path)

            compressed = repository.compress_file.compress(test_file_path)
            assert blobs[0]["data"] == compressed
            assert blobs[0]["size"] == test_file_path.stat().st_size

    def test_add_index_with_same_content_multiple_files(
        self, sqlite: SQLite, repository: Repository, test_directory: Path
    ):
        repository.init()

        with patch("os.getcwd", return_value=test_directory.as_posix()):
            _, path1 = tempfile.mkstemp(dir=test_directory)
            _, path2 = tempfile.mkstemp(dir=test_directory)

            result = repository.add_index([Path(path1).name, Path(path2).name])
            assert result.success is True

            entries = sqlite.select(f"SELECT * FROM {IndexEntry.table_name()}")
            assert len(entries) == 2
            assert entries[0]["object_id"] == entries[1]["object_id"]

            blobs = sqlite.select(f"SELECT * FROM {Blob.table_name()}")
            assert len(blobs) == 1
            assert entries[0]["object_id"] == blobs[0]["object_id"]

    def test_add_index_with_multiple_files(
        self, sqlite: SQLite, repository: Repository, test_directory: Path
    ):
        repository.init()

        with patch("os.getcwd", return_value=test_directory.as_posix()):
            _, path1 = tempfile.mkstemp(dir=test_directory)
            _, path2 = tempfile.mkstemp(dir=test_directory)
            Path(path2).write_bytes(b"append_data")

            result = repository.add_index([Path(path1).name, Path(path2).name])
            assert result.success is True

            entries = sqlite.select(f"SELECT * FROM {IndexEntry.table_name()}")
            assert len(entries) == 2

            blobs = sqlite.select(f"SELECT * FROM {Blob.table_name()}")
            assert len(blobs) == 2

    def test_add_index_with_mutiple_files_in_directory(
        self, sqlite: SQLite, repository: Repository, test_directory: Path
    ):
        repository.init()

        with patch("os.getcwd", return_value=test_directory.parent.as_posix()):
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

    def test_add_index_with_large_file(
        self,
        sqlite: SQLite,
        repository: Repository,
        test_directory: Path,
        test_large_file_path: Path,
    ):
        repository.init()

        with patch("os.getcwd", return_value=test_directory.as_posix()):
            result = repository.add_index([test_large_file_path.name])
            compressed = repository.compress_file.compress(test_large_file_path)

            assert result.success is True

            entries = sqlite.select(f"SELECT * FROM {IndexEntry.table_name()}")
            assert len(entries) == 1
            assert entries[0]["size"] == test_large_file_path.stat().st_size

            blobs = sqlite.select(f"SELECT * FROM {Blob.table_name()}")
            assert len(blobs) == 1
            assert blobs[0]["object_id"] == repository.hash_file.hash(test_large_file_path)
            assert blobs[0]["data"] == compressed
            assert blobs[0]["size"] == test_large_file_path.stat().st_size

    def test_add_index_when_update_file_index_entry_replacement(
        self, sqlite: SQLite, repository: Repository, test_directory: Path
    ):
        repository.init()

        with patch("os.getcwd", return_value=test_directory.as_posix()):
            _, path = tempfile.mkstemp(dir=test_directory)
            path = Path(path)
            repository.add_index([path.name])

            entries = sqlite.select(f"SELECT * FROM {IndexEntry.table_name()}")
            assert len(entries) == 1

            blobs = sqlite.select(f"SELECT * FROM {Blob.table_name()}")
            assert len(blobs) == 1
            assert entries[0]["object_id"] == blobs[0]["object_id"]

            path.write_bytes(b"update data")
            result = repository.add_index([path.name])

            assert result.success is True

            entries = sqlite.select(f"SELECT * FROM {IndexEntry.table_name()}")
            assert len(entries) == 1

            blobs = sqlite.select(
                f"SELECT * FROM {Blob.table_name()} ORDER BY created_at ASC"
            )
            assert len(blobs) == 2
            assert entries[0]["object_id"] == blobs[1]["object_id"]

    def test_add_index_when_add_new_and_update_file(
        self, sqlite: SQLite, repository: Repository, test_directory: Path
    ):
        repository.init()

        with patch("os.getcwd", return_value=test_directory.as_posix()):
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

    def test_add_index_when_add_completed_same_file(
        self, sqlite: SQLite, repository: Repository, test_directory: Path
    ):
        repository.init()

        with patch("os.getcwd", return_value=test_directory.as_posix()):
            _, path = tempfile.mkstemp(dir=test_directory)
            path = Path(path)

            repository.add_index([path.name])
            repository.add_index([path.name])

            entries = sqlite.select(f"SELECT * FROM {IndexEntry.table_name()}")
            assert len(entries) == 1

            blobs = sqlite.select(f"SELECT * FROM {Blob.table_name()}")
            assert len(blobs) == 1

    def test_add_index_duplicate_paths_in_single_call(
        self, sqlite: SQLite, repository: Repository, test_directory: Path
    ):
        repository.init()

        with patch("os.getcwd", return_value=test_directory.as_posix()):
            _, path = tempfile.mkstemp(dir=test_directory)
            path = Path(path)

            repository.add_index([path.name, path.name])

            entries = sqlite.select(f"SELECT * FROM {IndexEntry.table_name()}")
            assert len(entries) == 1

            blobs = sqlite.select(f"SELECT * FROM {Blob.table_name()}")
            assert len(blobs) == 1


class TestRepositoryStatus:
    """Test cases for Repository status functionality."""

    def test_status_in_uninitialized_repository(self, repository: Repository):
        """Test status in uninitialized repository returns error."""
        result = repository.status()
        assert result.failed is True
        assert result.error == "Not a gitoy repository"

    def test_status_empty_repository(self, repository: Repository):
        """Test status in empty initialized repository."""
        repository.init()
        result = repository.status()

        assert result.success is True
        status_result = result.value
        assert status_result is not None
        assert status_result.branch_name == "main"
        assert status_result.unstaged is not None
        assert status_result.staged is not None
        assert status_result.unstaged.modified == []
        assert status_result.unstaged.deleted == []
        assert status_result.unstaged.added == []

    def test_status_with_untracked_files(
        self, repository: Repository, test_directory: Path
    ):
        """Test status shows untracked files."""
        repository.init()

        with patch("os.getcwd", return_value=test_directory.as_posix()):
            _, path1 = tempfile.mkstemp(dir=test_directory)
            _, path2 = tempfile.mkstemp(dir=test_directory)
            path1 = Path(path1)
            path2 = Path(path2)

            result = repository.status()

            assert result.success is True
            status_result = result.value
            assert status_result is not None
            assert status_result.unstaged is not None
            assert status_result.staged is not None
            assert path1 in [
                entry.absolute_path(repository.worktree_path)
                for entry in status_result.unstaged.added
            ]
            assert path2 in [
                entry.absolute_path(repository.worktree_path)
                for entry in status_result.unstaged.added
            ]
            assert len(status_result.unstaged.added) == 2

    def test_status_with_unstaged_modified_files(
        self, repository: Repository, test_directory: Path
    ):
        """Test status shows unstaged modified files."""
        repository.init()

        with patch("os.getcwd", return_value=test_directory.as_posix()):
            _, path = tempfile.mkstemp(dir=test_directory)
            path = Path(path)

            repository.add_index([path.name])

            path.write_bytes(b"modified content")

            result = repository.status()

            assert result.success is True
            status_result = result.value
            assert status_result is not None
            assert status_result.unstaged is not None
            assert status_result.staged is not None
            assert path in [
                entry.absolute_path(repository.worktree_path)
                for entry in status_result.unstaged.modified
            ]
            assert status_result.unstaged.deleted == []
            assert status_result.unstaged.added == []

    def test_status_with_unstaged_deleted_files(
        self, repository: Repository, test_directory: Path
    ):
        """Test status shows unstaged deleted files."""
        repository.init()

        with patch("os.getcwd", return_value=test_directory.as_posix()):
            _, path = tempfile.mkstemp(dir=test_directory)
            path = Path(path)
            path_name = path.name

            repository.add_index([path_name])

            path.unlink()

            result = repository.status()

            assert result.success is True
            status_result = result.value
            assert status_result is not None
            assert status_result.unstaged is not None
            assert status_result.staged is not None
            assert path in [
                entry.absolute_path(repository.worktree_path)
                for entry in status_result.unstaged.deleted
            ]
            assert status_result.unstaged.modified == []
            assert status_result.unstaged.added == []

    def test_status_mixed_file_states(
        self, repository: Repository, test_directory: Path
    ):
        """Test status with mixed file states."""
        repository.init()

        with patch("os.getcwd", return_value=test_directory.as_posix()):
            _, untracked_path = tempfile.mkstemp(dir=test_directory)
            _, modified_path = tempfile.mkstemp(dir=test_directory)
            _, deleted_path = tempfile.mkstemp(dir=test_directory)

            untracked_path = Path(untracked_path)
            modified_path = Path(modified_path)
            deleted_path = Path(deleted_path)

            repository.add_index([modified_path.name, deleted_path.name])

            modified_path.write_bytes(b"modified content")
            deleted_path.unlink()

            result = repository.status()

            assert result.success is True
            status_result = result.value
            assert status_result is not None
            assert status_result.unstaged is not None
            assert status_result.staged is not None
            assert untracked_path in [
                entry.absolute_path(repository.worktree_path)
                for entry in status_result.unstaged.added
            ]
            assert modified_path in [
                entry.absolute_path(repository.worktree_path)
                for entry in status_result.unstaged.modified
            ]
            assert deleted_path in [
                entry.absolute_path(repository.worktree_path)
                for entry in status_result.unstaged.deleted
            ]

    def test_status_mixed_file_states_2(
        self, repository: Repository, test_directory: Path, test_repo_directory: Path
    ):
        """Test status with mixed file states."""
        repository.init()

        with patch("os.getcwd", return_value=test_directory.as_posix()):
            _, untracked_path = tempfile.mkstemp(dir=test_repo_directory)
            _, untracked_path2 = tempfile.mkstemp(dir=test_repo_directory)
            _, modified_path = tempfile.mkstemp(dir=test_directory)
            _, deleted_path = tempfile.mkstemp(dir=test_directory)

            untracked_path = Path(untracked_path)
            untracked_path2 = Path(untracked_path2)
            modified_path = Path(modified_path)
            deleted_path = Path(deleted_path)

            repository.add_index([modified_path.name, deleted_path.name])

            modified_path.write_bytes(b"modified content")
            deleted_path.unlink()

            result = repository.status()

            assert result.success is True
            status_result = result.value
            assert status_result is not None
            assert status_result.unstaged is not None
            assert status_result.staged is not None
            assert untracked_path in [
                entry.absolute_path(repository.worktree_path)
                for entry in status_result.unstaged.added
            ]
            assert untracked_path2 in [
                entry.absolute_path(repository.worktree_path)
                for entry in status_result.unstaged.added
            ]
            assert modified_path in [
                entry.absolute_path(repository.worktree_path)
                for entry in status_result.unstaged.modified
            ]
            assert deleted_path in [
                entry.absolute_path(repository.worktree_path)
                for entry in status_result.unstaged.deleted
            ]


class TestRepositoryCommit:
    def test_no_update_commit(
        self, repository: Repository, database: Database, tree_store: TreeStore
    ):
        repository.init()

        commit = repository.commit("Initial commit")

        assert commit is None

        index_entries = [
            IndexEntry(
                path="./new_file.txt",
                object_id="blob_123",
                mode="100644",
                size=100,
            ),
        ]

        database.create_index_entries(index_entries)

        first_commit = repository.commit("Initial commit")
        assert first_commit is not None

        second_commit = repository.commit("Second commit")
        assert second_commit is None

    def test_initial_commit(
        self, repository: Repository, database: Database, tree_store: TreeStore
    ):
        repository.init()

        index_entries = [
            IndexEntry(
                path="./new_file.txt",
                object_id="blob_123",
                mode="100644",
                size=100,
            ),
        ]

        database.create_index_entries(index_entries)

        commit = repository.commit("Initial commit")

        # 해드 브랜치 업데이트가 됐는가?
        head = database.get_head_branch()
        assert head.target_object_id == commit.object_id

        # 커밋이 잘 저장됐는가?
        db_commit = database.get_commit(commit.object_id)
        assert db_commit is not None

        # 트리가 잘 저장됐는가?
        tree = tree_store.build_commit_tree(db_commit.tree_id)

        assert tree is not None
        assert tree.root_entry is not None
        assert tree.entry_count == 2
        assert tree.get_entry(".") is not None
        assert tree.get_entry("./new_file.txt") is not None

        tree_entries_db = database.sqlite.select(
            f"SELECT * FROM {TreeEntry.table_name()}"
        )
        assert len(tree_entries_db) == 2

    def test_inital_commit_when_duplicate_structure(
        self, repository: Repository, database: Database, tree_store: TreeStore
    ):
        repository.init()

        index_entries = [
            IndexEntry(
                path="./new_file.txt",
                object_id="blob_123",
                mode="100644",
                size=100,
            ),
            IndexEntry(
                path="./a/new_file.txt",
                object_id="blob_123",
                mode="100644",
                size=100,
            ),
        ]

        database.create_index_entries(index_entries)

        commit = repository.commit("Initial commit")

        # 커밋이 잘 저장됐는가?
        db_commit = database.get_commit(commit.object_id)
        assert db_commit is not None

        # 트리가 잘 저장됐는가?

        tree = tree_store.build_commit_tree(db_commit.tree_id)

        assert tree is not None
        assert tree.root_entry is not None
        assert tree.entry_count == 4
        assert tree.get_entry(".") is not None
        assert tree.get_entry("./new_file.txt") is not None
        assert tree.get_entry("./a") is not None
        assert tree.get_entry("./a/new_file.txt") is not None

        tree_entries_db = database.sqlite.select(
            f"SELECT * FROM {TreeEntry.table_name()}"
        )
        assert len(tree_entries_db) == 4

    def test_second_commit_on_add_file(
        self, repository: Repository, database: Database, tree_store: TreeStore
    ):
        repository.init()
        index_entries = [
            IndexEntry(
                path="./new_file.txt",
                object_id="blob_123",
                mode="100644",
                size=100,
            ),
        ]
        database.create_index_entries(index_entries)
        first_commit = repository.commit("Initial commit")

        index_entries2 = [
            IndexEntry(
                path="./new_file2.txt",
                object_id="blob_123",
                mode="100644",
                size=100,
            ),
        ]
        database.create_index_entries(index_entries2)
        second_commit = repository.commit("Add new file")

        # 해드 브랜치 업데이트가 됐는가?
        head = database.get_head_branch()
        assert head.target_object_id == second_commit.object_id

        # 커밋이 잘 저장됐는가?
        db_commit = database.get_commit(second_commit.object_id)
        assert db_commit is not None
        assert db_commit.message == "Add new file"
        commits = database.sqlite.select(f"SELECT * FROM {Commit.table_name()}")
        assert len(commits) == 2

        # 트리가 잘 저장됐는가?
        tree = tree_store.build_commit_tree(db_commit.tree_id)

        assert tree is not None
        assert tree.root_entry is not None
        assert tree.entry_count == 3
        assert tree.get_entry(".") is not None
        assert tree.get_entry("./new_file.txt") is not None
        assert tree.get_entry("./new_file2.txt") is not None

        tree_entries_db = database.sqlite.select(
            f"SELECT * FROM {TreeEntry.table_name()}"
        )
        assert len(tree_entries_db) == 5

        # 이전 커밋 트리가 잘 불러와지는지?
        tree = tree_store.build_commit_tree(first_commit.tree_id)

        assert tree is not None
        assert tree.root_entry is not None
        assert tree.entry_count == 2
        assert tree.get_entry(".") is not None
        assert tree.get_entry("./new_file.txt") is not None

    def test_second_commit_on_add_dir(
        self, repository: Repository, database: Database, tree_store: TreeStore
    ):
        repository.init()
        index_entries = [
            IndexEntry(
                path="./new_file.txt",
                object_id="blob_123",
                mode="100644",
                size=100,
            ),
        ]
        database.create_index_entries(index_entries)
        first_commit = repository.commit("Initial commit")

        index_entries2 = [
            IndexEntry(
                path="./dir/new_file.txt",
                object_id="blob_123",
                mode="100644",
                size=100,
            ),
        ]
        database.create_index_entries(index_entries2)
        second_commit = repository.commit("Add new dir and file")

        # 해드 브랜치 업데이트가 됐는가?
        head = database.get_head_branch()
        assert head.target_object_id == second_commit.object_id

        # 커밋이 잘 저장됐는가?
        db_commit = database.get_commit(second_commit.object_id)
        assert db_commit is not None
        assert db_commit.message == "Add new dir and file"
        commits = database.sqlite.select(f"SELECT * FROM {Commit.table_name()}")
        assert len(commits) == 2

        # 트리가 잘 저장됐는가?
        tree = tree_store.build_commit_tree(db_commit.tree_id)

        assert tree is not None
        assert tree.root_entry is not None
        assert tree.entry_count == 4
        assert tree.get_entry(".") is not None
        assert tree.get_entry("./new_file.txt") is not None
        assert tree.get_entry("./dir/new_file.txt") is not None

        tree_entries_db = database.sqlite.select(
            f"SELECT * FROM {TreeEntry.table_name()}"
        )
        assert len(tree_entries_db) == 5

        # 이전 커밋 트리가 잘 불러와지는지?
        tree = tree_store.build_commit_tree(first_commit.tree_id)

        assert tree is not None
        assert tree.root_entry is not None
        assert tree.entry_count == 2
        assert tree.get_entry(".") is not None
        assert tree.get_entry("./new_file.txt") is not None

    def test_second_commit_on_delete_file(
        self, repository: Repository, database: Database, tree_store: TreeStore
    ):
        repository.init()
        index_entries = [
            IndexEntry(
                path="./new_file.txt",
                object_id="blob_123",
                mode="100644",
                size=100,
            ),
            IndexEntry(
                path="./new_file2.txt",
                object_id="blob_123",
                mode="100644",
                size=100,
            ),
        ]
        database.create_index_entries(index_entries)
        first_commit = repository.commit("Initial commit")

        database.delete_index_entries([index_entries[1]])

        second_commit = repository.commit("Second commit")

        # 해드 브랜치 업데이트가 됐는가?
        head = database.get_head_branch()
        assert head.target_object_id == second_commit.object_id

        # 커밋이 잘 저장됐는가?
        db_commit = database.get_commit(second_commit.object_id)
        assert db_commit is not None
        assert db_commit.message == "Second commit"
        commits = database.sqlite.select(f"SELECT * FROM {Commit.table_name()}")
        assert len(commits) == 2

        # 트리가 잘 저장됐는가?
        tree = tree_store.build_commit_tree(db_commit.tree_id)

        assert tree is not None
        assert tree.root_entry is not None
        assert tree.entry_count == 2
        assert tree.get_entry(".") is not None
        assert tree.get_entry("./new_file.txt") is not None

        # 이전 커밋 트리가 잘 불러와지는지?
        tree = tree_store.build_commit_tree(first_commit.tree_id)

        assert tree is not None
        assert tree.root_entry is not None
        assert tree.entry_count == 3
        assert tree.get_entry(".") is not None
        assert tree.get_entry("./new_file.txt") is not None
        assert tree.get_entry("./new_file2.txt") is not None

    def test_second_commit_on_delete_directory(
        self, repository: Repository, database: Database, tree_store: TreeStore
    ):
        repository.init()
        index_entries = [
            IndexEntry(
                path="./new_file.txt",
                object_id="blob_123",
                mode="100644",
                size=100,
            ),
            IndexEntry(
                path="./dir/new_file.txt",
                object_id="blob_123",
                mode="100644",
                size=100,
            ),
        ]
        database.create_index_entries(index_entries)
        first_commit = repository.commit("Initial commit")

        database.delete_index_entries([index_entries[1]])

        second_commit = repository.commit("Second commit")

        # 해드 브랜치 업데이트가 됐는가?
        head = database.get_head_branch()
        assert head.target_object_id == second_commit.object_id

        # 커밋이 잘 저장됐는가?
        db_commit = database.get_commit(second_commit.object_id)
        assert db_commit is not None
        assert db_commit.message == "Second commit"
        commits = database.sqlite.select(f"SELECT * FROM {Commit.table_name()}")
        assert len(commits) == 2

        # 트리가 잘 저장됐는가?
        tree = tree_store.build_commit_tree(db_commit.tree_id)

        assert tree is not None
        assert tree.root_entry is not None
        assert tree.entry_count == 2
        assert tree.get_entry(".") is not None
        assert tree.get_entry("./new_file.txt") is not None

        tree_entries = database.sqlite.select(f"SELECT * FROM {TreeEntry.table_name()}")
        assert len(tree_entries) == 5

        # 이전 커밋 트리가 잘 불러와지는지?
        tree = tree_store.build_commit_tree(first_commit.tree_id)

        assert tree is not None
        assert tree.root_entry is not None
        assert tree.entry_count == 4
        assert tree.get_entry(".") is not None
        assert tree.get_entry("./new_file.txt") is not None
        assert tree.get_entry("./dir") is not None
        assert tree.get_entry("./dir/new_file.txt") is not None

    def test_second_commit_on_modified_directory(
        self, repository: Repository, database: Database, tree_store: TreeStore
    ):
        repository.init()
        index_entries = [
            IndexEntry(
                path="./new_file.txt",
                object_id="blob_123",
                mode="100644",
                size=100,
            ),
            IndexEntry(
                path="./dir/new_file.txt",
                object_id="blob_123",
                mode="100644",
                size=100,
            ),
        ]
        database.create_index_entries(index_entries)
        first_commit = repository.commit("Initial commit")

        # file modified
        database.delete_index_entries([index_entries[1]])
        index_entries[1].object_id = "updated_blob_123"
        database.create_index_entries([index_entries[1]])

        second_commit = repository.commit("Second commit")

        # 해드 브랜치 업데이트가 됐는가?
        head = database.get_head_branch()
        assert head.target_object_id == second_commit.object_id

        # 커밋이 잘 저장됐는가?
        db_commit = database.get_commit(second_commit.object_id)
        assert db_commit is not None
        assert db_commit.message == "Second commit"
        commits = database.sqlite.select(f"SELECT * FROM {Commit.table_name()}")
        assert len(commits) == 2

        # 트리가 잘 저장됐는가?
        tree = tree_store.build_commit_tree(db_commit.tree_id)

        assert tree is not None
        assert tree.root_entry is not None
        assert tree.entry_count == 4
        assert tree.get_entry(".") is not None
        assert tree.get_entry("./new_file.txt") is not None
        assert tree.get_entry("./dir") is not None
        assert (
            tree.get_entry("./dir/new_file.txt").entry_object_id == "updated_blob_123"
        )

        tree_entries = database.sqlite.select(f"SELECT * FROM {TreeEntry.table_name()}")
        assert len(tree_entries) == 8

        # 이전 커밋 트리가 잘 불러와지는지?
        tree = tree_store.build_commit_tree(first_commit.tree_id)

        assert tree is not None
        assert tree.root_entry is not None
        assert tree.entry_count == 4
        assert tree.get_entry(".") is not None
        assert tree.get_entry("./new_file.txt") is not None
        assert tree.get_entry("./dir") is not None
        assert tree.get_entry("./dir/new_file.txt").entry_object_id == "blob_123"

    def test_second_commit_on_modified_directory_name(
        self, repository: Repository, database: Database, tree_store: TreeStore
    ):
        repository.init()
        index_entries = [
            IndexEntry(
                path="./new_file.txt",
                object_id="blob_123",
                mode="100644",
                size=100,
            ),
            IndexEntry(
                path="./dir/new_file.txt",
                object_id="blob_123",
                mode="100644",
                size=100,
            ),
        ]
        database.create_index_entries(index_entries)
        first_commit = repository.commit("Initial commit")

        # file modified
        database.delete_index_entries([index_entries[1]])
        index_entries[1].path = "./dir2/new_file.txt"
        database.create_index_entries([index_entries[1]])

        second_commit = repository.commit("Second commit")

        # 해드 브랜치 업데이트가 됐는가?
        head = database.get_head_branch()
        assert head.target_object_id == second_commit.object_id

        # 커밋이 잘 저장됐는가?
        db_commit = database.get_commit(second_commit.object_id)
        assert db_commit is not None
        assert db_commit.message == "Second commit"
        commits = database.sqlite.select(f"SELECT * FROM {Commit.table_name()}")
        assert len(commits) == 2

        # 트리가 잘 저장됐는가?
        tree = tree_store.build_commit_tree(db_commit.tree_id)

        assert tree is not None
        assert tree.root_entry is not None
        assert tree.entry_count == 4
        assert tree.get_entry(".") is not None
        assert tree.get_entry("./new_file.txt") is not None
        assert tree.get_entry("./dir2") is not None
        assert tree.get_entry("./dir2/new_file.txt") is not None

        tree_entries = database.sqlite.select(f"SELECT * FROM {TreeEntry.table_name()}")
        assert len(tree_entries) == 7

        # 이전 커밋 트리가 잘 불러와지는지?
        tree = tree_store.build_commit_tree(first_commit.tree_id)

        assert tree is not None
        assert tree.root_entry is not None
        assert tree.entry_count == 4
        assert tree.get_entry(".") is not None
        assert tree.get_entry("./new_file.txt") is not None
        assert tree.get_entry("./dir") is not None
        assert tree.get_entry("./dir/new_file.txt") is not None

    def test_second_commit_on_mixed_operation(
        self, repository: Repository, database: Database, tree_store: TreeStore
    ):
        repository.init()
        index_entries = [
            IndexEntry(
                path="./new_file.txt",
                object_id="new_file_blob",
                mode="100644",
                size=100,
            ),
            IndexEntry(
                path="./new_file2.txt",
                object_id="new_file2_blob",
                mode="100644",
                size=100,
            ),
        ]
        database.create_index_entries(index_entries)
        first_commit = repository.commit("Initial commit")

        # file add delete and modified
        database.delete_index_entries(index_entries)
        index_entries[1].object_id = "blob_789"
        update_index_entries = [
            index_entries[1],
            IndexEntry(
                path="./new_file3.txt",
                object_id="new_file3_blob",
                mode="100644",
                size=100,
            ),
        ]

        database.create_index_entries(update_index_entries)

        second_commit = repository.commit("Second commit")

        # 해드 브랜치 업데이트가 됐는가?
        head = database.get_head_branch()
        assert head.target_object_id == second_commit.object_id

        # 커밋이 잘 저장됐는가?
        db_commit = database.get_commit(second_commit.object_id)
        assert db_commit is not None
        assert db_commit.message == "Second commit"
        commits = database.sqlite.select(f"SELECT * FROM {Commit.table_name()}")
        assert len(commits) == 2

        # 트리가 잘 저장됐는가?
        tree = tree_store.build_commit_tree(db_commit.tree_id)

        assert tree is not None
        assert tree.root_entry is not None
        assert tree.entry_count == 3
        assert tree.get_entry(".") is not None
        assert tree.get_entry("./new_file2.txt") is not None
        assert tree.get_entry("./new_file3.txt") is not None

        tree_entries = database.sqlite.select(f"SELECT * FROM {TreeEntry.table_name()}")
        assert len(tree_entries) == 6

        # 이전 커밋 트리가 잘 불러와지는지?
        tree = tree_store.build_commit_tree(first_commit.tree_id)

        assert tree is not None
        assert tree.root_entry is not None
        assert tree.entry_count == 3
        assert tree.get_entry(".") is not None
        assert tree.get_entry("./new_file.txt") is not None
        assert tree.get_entry("./new_file2.txt") is not None

    def test_commit_parent_relations(
        self, repository: Repository, database: Database, tree_store: TreeStore
    ):
        repository.init()
        index_entries = [
            IndexEntry(
                path="./new_file.txt",
                object_id="new_file_blob",
                mode="100644",
                size=100,
            ),
        ]
        database.create_index_entries(index_entries)
        first_commit = repository.commit("Initial commit")

        index_entries2 = [
            IndexEntry(
                path="./new_file2.txt",
                object_id="new_file_blob",
                mode="100644",
                size=100,
            ),
        ]
        database.create_index_entries(index_entries2)
        second_commit = repository.commit("Second commit")

        index_entries3 = [
            IndexEntry(
                path="./new_file3.txt",
                object_id="new_file_blob",
                mode="100644",
                size=100,
            ),
        ]
        database.create_index_entries(index_entries3)
        third_commit = repository.commit("Third commit")

        commit_children = database.get_commit_children(first_commit.object_id)
        assert len(commit_children) == 1
        assert commit_children[0].commit_id == second_commit.object_id

        commit_children = database.get_commit_children(second_commit.object_id)
        assert len(commit_children) == 1
        assert commit_children[0].commit_id == third_commit.object_id

        commit_children = database.get_commit_children(third_commit.object_id)
        assert len(commit_children) == 0


class TestRepositoryCompareIndexToWorktree:
    def test_diff_added(
        self,
        repository: Repository,
        repository_path: RepositoryPath,
        convert: Convert,
        test_file_path: Path,
    ):
        repository.init()

        with mock.patch(
            "os.getcwd", return_value=repository_path.worktree_path.as_posix()
        ):
            result = repository.get_unstaged_changes([test_file_path.parent.name])
            assert len(result.added) == 1
            assert result.added[0] == convert.path_to_index_entry(test_file_path)
            assert result.deleted == []
            assert result.modified == []

    def test_diff_deleted(
        self,
        repository: Repository,
        convert: Convert,
        database: Database,
        test_directory: Path,
    ):
        repository.init()

        with mock.patch("os.getcwd", return_value=test_directory.as_posix()):
            _, _path = tempfile.mkstemp(dir=test_directory)
            path = Path(_path)
            index_entry = convert.path_to_index_entry(path)
            database.create_index_entries([index_entry])

            path.unlink()

            result = repository.get_unstaged_changes([_path])
            assert result.added == []
            assert len(result.deleted) == 1
            assert result.deleted[0] == index_entry
            assert result.modified == []

    def test_diff_modified(
        self,
        repository: Repository,
        convert: Convert,
        database: Database,
        test_directory: Path,
    ):
        repository.init()

        with mock.patch("os.getcwd", return_value=test_directory.as_posix()):
            _, _path = tempfile.mkstemp(dir=test_directory)
            path = Path(_path)
            index_entry = convert.path_to_index_entry(path)
            database.create_index_entries([index_entry])

            path.write_text("modified")

            result = repository.get_unstaged_changes([_path])
            assert result.added == []
            assert result.deleted == []
            assert len(result.modified) == 1
            assert result.modified[0] == convert.path_to_index_entry(path)

    def test_diff_mixed(
        self,
        repository: Repository,
        convert: Convert,
        database: Database,
        test_directory: Path,
    ):
        repository.init()

        with mock.patch("os.getcwd", return_value=test_directory.as_posix()):
            _, _path = tempfile.mkstemp(dir=test_directory)
            path = Path(_path)
            index_entry = convert.path_to_index_entry(path)
            database.create_index_entries([index_entry])
            path.write_text("modified")

            _, _path2 = tempfile.mkstemp(dir=test_directory)

            result = repository.get_unstaged_changes([_path, _path2])
            assert len(result.added) == 1
            assert result.added[0] == convert.path_to_index_entry(Path(_path2))
            assert result.deleted == []
            assert len(result.modified) == 1
            assert result.modified[0] == convert.path_to_index_entry(path)

            path.unlink()

            result = repository.get_unstaged_changes([_path, _path2])
            assert len(result.added) == 1
            assert len(result.deleted) == 1
            assert len(result.modified) == 0

            path2 = Path(_path2)
            index_entry2 = convert.path_to_index_entry(path2)
            database.create_index_entries([index_entry2])
            path2.write_text("modified")

            result = repository.get_unstaged_changes([_path, _path2])
            assert len(result.added) == 0
            assert len(result.deleted) == 1
            assert len(result.modified) == 1

            _, _path3 = tempfile.mkstemp(dir=test_directory)

            result = repository.get_unstaged_changes([_path, _path2, _path3])
            assert len(result.added) == 1
            assert len(result.deleted) == 1
            assert len(result.modified) == 1

            result = repository.get_unstaged_changes([_path, _path2])
            assert len(result.added) == 0
            assert len(result.deleted) == 1
            assert len(result.modified) == 1

            result = repository.get_unstaged_changes([_path2, _path3])
            assert len(result.added) == 1
            assert len(result.deleted) == 0
            assert len(result.modified) == 1

    def test_diff_path_changed(
        self,
        repository: Repository,
        convert: Convert,
        database: Database,
        test_directory: Path,
    ):
        repository.init()

        with mock.patch("os.getcwd", return_value=test_directory.as_posix()):
            _, _path = tempfile.mkstemp(dir=test_directory)
            path = Path(_path)
            index_entry = convert.path_to_index_entry(path)
            database.create_index_entries([index_entry])

            renamed = path.with_name("renamed")
            path.rename(renamed)

            result = repository.get_unstaged_changes([renamed.name])
            assert len(result.added) == 1
            assert result.added[0] == convert.path_to_index_entry(renamed)
            assert result.deleted == []
            assert result.modified == []

            result = repository.get_unstaged_changes(["."])
            assert len(result.added) == 1
            assert len(result.deleted) == 1
            assert result.modified == []

            result = repository.get_unstaged_changes([f"../{test_directory.name}"])
            assert len(result.added) == 1
            assert len(result.deleted) == 1
            assert result.modified == []

    def test_diff_on_check_duplicate_path(
        self,
        repository: Repository,
        convert: Convert,
        database: Database,
        test_directory: Path,
    ):
        repository.init()

        with mock.patch("os.getcwd", return_value=test_directory.as_posix()):
            _, _path = tempfile.mkstemp(dir=test_directory)
            path = Path(_path)
            index_entry = convert.path_to_index_entry(path)
            database.create_index_entries([index_entry])
            path.unlink()

            _, _path2 = tempfile.mkstemp(dir=test_directory)

            path2 = Path(_path2)
            index_entry2 = convert.path_to_index_entry(path2)
            database.create_index_entries([index_entry2])
            path2.write_text("modified")

            _, _path3 = tempfile.mkstemp(dir=test_directory)

            result = repository.get_unstaged_changes([_path, _path2, _path3, "./"])
            assert len(result.added) == 1
            assert len(result.deleted) == 1
            assert len(result.modified) == 1


class TestRepositoryCompareIndexToTree:
    """Test cases for Repository.compare_index_to_tree functionality."""

    def test_diff_with_empty_index_and_empty_tree(
        self, repository: Repository, database: Database, tree_store: TreeStore
    ):
        """Test diff with empty index and empty commit tree."""
        # Arrange
        repository.init()

        commit_datetime = datetime.datetime.now()
        sample_commit = Commit(
            tree_id="sample_tree_123",
            author_name="",
            author_email="",
            author_date=commit_datetime,
            committer_name="",
            committer_email="",
            message="Test commit",
            object_id="test_commit_123",
            committer_date=commit_datetime,
            created_at=commit_datetime,
            generation_number=0
        )

        # Act
        index_entries = database.list_index_entries()
        tree = tree_store.build_commit_tree(sample_commit.tree_id)
        result = repository.entry_diff.diff(index_entries, tree.list_index_entries())

        # Assert
        assert result is not None
        assert result.is_empty() is True
        assert len(result.added) == 0
        assert len(result.deleted) == 0
        assert len(result.modified) == 0

    def test_diff_with_files_added_to_index(
        self, repository: Repository, database: Database, tree_store: TreeStore
    ):
        # Arrange
        repository.init()

        commit_datetime = datetime.datetime.now()
        sample_commit = Commit(
            tree_id="sample_tree_123",
            author_name="",
            author_email="",
            author_date=commit_datetime,
            committer_name="",
            committer_email="",
            message="Test commit",
            object_id="test_commit_123",
            committer_date=commit_datetime,
            created_at=commit_datetime,
            generation_number=0
        )

        # Add files to index
        index_entries = [
            IndexEntry(
                path="new_file1.txt",
                object_id="blob_123",
                mode="100644",
                size=100,
            ),
            IndexEntry(
                path="new_file2.txt",
                object_id="blob_456",
                mode="100644",
                size=200,
            ),
        ]

        database.create_index_entries(index_entries)

        # Act
        index_entries = database.list_index_entries()
        tree = tree_store.build_commit_tree(sample_commit.tree_id)
        result = repository.entry_diff.diff(index_entries, tree.list_index_entries())

        # Assert
        assert result is not None
        assert result.is_empty() is False
        assert len(result.added) == 2
        assert len(result.deleted) == 0
        assert len(result.modified) == 0

        added_paths = [entry.path for entry in result.added]
        assert "new_file1.txt" in added_paths
        assert "new_file2.txt" in added_paths

    def test_diff_with_files_deleted_from_index(
        self, repository: Repository, database: Database, tree_store: TreeStore
    ):
        """Test diff when files exist in commit tree but not in index."""
        # Arrange
        repository.init()

        commit_datetime = datetime.datetime.now()
        sample_commit = Commit(
            tree_id="sample_tree_123",
            author_name="",
            author_email="",
            author_date=commit_datetime,
            committer_name="",
            committer_email="",
            message="Test commit",
            object_id="test_commit_123",
            committer_date=commit_datetime,
            created_at=commit_datetime,
            generation_number=0
        )

        database.create_commit(sample_commit)
        tree_id = sample_commit.tree_id

        # Create tree entries (files in commit)
        tree_entries = [
            TreeEntry(
                tree_id=tree_id,
                entry_name="deleted_file1.txt",
                entry_mode="100644",
                entry_object_id="blob_789",
                entry_type="blob",
            ),
            TreeEntry(
                tree_id=tree_id,
                entry_name="deleted_file2.txt",
                entry_mode="100644",
                entry_object_id="blob_101112",
                entry_type="blob",
            ),
        ]

        database.create_tree_entries(tree_entries)

        # Add root tree entry
        database.sqlite.insert(
            TreeEntry(
                tree_id="",
                entry_name=".",
                entry_mode="040000",
                entry_object_id=tree_id,
                entry_type="tree",
            )
        )

        # Act
        index_entries = database.list_index_entries()
        tree = tree_store.build_commit_tree(sample_commit.tree_id)
        result = repository.entry_diff.diff(index_entries, tree.list_index_entries())

        assert result is not None
        assert result.is_empty() is False
        assert len(result.added) == 0
        assert len(result.deleted) == 2
        assert len(result.modified) == 0

    def test_diff_with_modified_files(
        self, repository: Repository, database: Database, tree_store: TreeStore
    ):
        """Test diff when files are modified (different object_id or mode)."""
        # Arrange
        repository.init()

        commit_datetime = datetime.datetime.now()
        sample_commit = Commit(
            tree_id="sample_tree_123",
            author_name="",
            author_email="",
            author_date=commit_datetime,
            committer_name="",
            committer_email="",
            message="Test commit",
            object_id="test_commit_123",
            committer_date=commit_datetime,
            created_at=commit_datetime,
            generation_number=0
        )

        database.sqlite.insert(sample_commit)
        tree_id = sample_commit.tree_id

        # Add files to index
        index_entries = [
            IndexEntry(
                path="./modified_file1.txt",
                object_id="blob_new_123",  # Different object_id
                mode="100644",
                size=100,
            ),
            IndexEntry(
                path="./modified_file2.txt",
                object_id="blob_456",
                mode="100755",  # Different file_mode
                size=200,
            ),
        ]

        # Create corresponding tree entries with different values
        tree_entries = [
            TreeEntry(
                tree_id=tree_id,
                entry_name="modified_file1.txt",
                entry_mode="100644",
                entry_object_id="blob_old_123",  # Different object_id
                entry_type="blob",
            ),
            TreeEntry(
                tree_id=tree_id,
                entry_name="modified_file2.txt",
                entry_mode="100644",  # Different file_mode
                entry_object_id="blob_456",
                entry_type="blob",
            ),
        ]

        database.create_index_entries(index_entries)
        database.sqlite.insert_many(tree_entries)

        # Add root tree entry
        database.sqlite.insert(
            TreeEntry(
                tree_id="",
                entry_name=".",
                entry_mode="040000",
                entry_object_id=tree_id,
                entry_type="tree",
            )
        )

        # Act
        index_entries = database.list_index_entries()
        tree = tree_store.build_commit_tree(sample_commit.tree_id)
        result = repository.entry_diff.diff(index_entries, tree.list_index_entries())

        # Assert
        assert result is not None
        assert result.is_empty() is False
        assert len(result.added) == 0
        assert len(result.deleted) == 0
        assert len(result.modified) == 2

        modified_paths = [entry.path for entry in result.modified]
        assert "./modified_file1.txt" in modified_paths
        assert "./modified_file2.txt" in modified_paths

    def test_diff_with_unchanged_files(
        self, repository: Repository, database: Database, tree_store: TreeStore
    ):
        """Test diff when files are unchanged between index and commit."""
        # Arrange
        repository.init()

        commit_datetime = datetime.datetime.now()
        sample_commit = Commit(
            tree_id="sample_tree_123",
            author_name="",
            author_email="",
            author_date=commit_datetime,
            committer_name="",
            committer_email="",
            message="Test commit",
            object_id="test_commit_123",
            committer_date=commit_datetime,
            created_at=commit_datetime,
            generation_number=0
        )

        database.sqlite.insert(sample_commit)
        tree_id = sample_commit.tree_id

        # Add files to index
        index_entries = [
            IndexEntry(
                path="./unchanged_file.txt",
                object_id="blob_same",
                mode="100644",
                size=100,
            )
        ]

        # Create corresponding tree entry with same values
        tree_entries = [
            TreeEntry(
                tree_id=tree_id,
                entry_name="unchanged_file.txt",
                entry_mode="100644",
                entry_object_id="blob_same",
                entry_type="blob",
            )
        ]

        database.sqlite.insert_many(index_entries)
        database.sqlite.insert_many(tree_entries)

        # Add root tree entry
        database.sqlite.insert(
            TreeEntry(
                tree_id="",
                entry_name=".",
                entry_mode="040000",
                entry_object_id=tree_id,
                entry_type="tree",
            )
        )

        # Act
        index_entries = database.list_index_entries()
        tree = tree_store.build_commit_tree(sample_commit.tree_id)
        result = repository.entry_diff.diff(index_entries, tree.list_index_entries())

        # Assert
        assert result is not None
        assert result.is_empty() is True
        assert len(result.added) == 0
        assert len(result.deleted) == 0
        assert len(result.modified) == 0

    def test_diff_with_mixed_changes(
        self, repository: Repository, database: Database, tree_store: TreeStore
    ):
        """Test diff with a combination of added, modified, and deleted files."""
        # Arrange
        repository.init()

        commit_datetime = datetime.datetime.now()
        sample_commit = Commit(
            tree_id="sample_tree_123",
            author_name="",
            author_email="",
            author_date=commit_datetime,
            committer_name="",
            committer_email="",
            message="Test commit",
            object_id="test_commit_123",
            committer_date=commit_datetime,
            created_at=commit_datetime,
            generation_number=0
        )

        database.sqlite.insert(sample_commit)
        tree_id = sample_commit.tree_id

        # Files in index: added + modified + unchanged
        index_entries = [
            # Added file (not in tree)
            IndexEntry(
                path="./added_file.txt",
                object_id="blob_added",
                mode="100644",
                size=100,
            ),
            # Modified file (different content)
            IndexEntry(
                path="./modified_file.txt",
                object_id="blob_modified_new",
                mode="100644",
                size=200,
            ),
            # Unchanged file
            IndexEntry(
                path="./unchanged_file.txt",
                object_id="blob_unchanged",
                mode="100644",
                size=300,
            ),
        ]

        # Files in tree: deleted + modified + unchanged
        tree_entries = [
            # Deleted file (not in index)
            TreeEntry(
                tree_id=tree_id,
                entry_name="deleted_file.txt",
                entry_mode="100644",
                entry_object_id="blob_deleted",
                entry_type="blob",
            ),
            # Modified file (old content)
            TreeEntry(
                tree_id=tree_id,
                entry_name="modified_file.txt",
                entry_mode="100644",
                entry_object_id="blob_modified_old",
                entry_type="blob",
            ),
            # Unchanged file
            TreeEntry(
                tree_id=tree_id,
                entry_name="unchanged_file.txt",
                entry_mode="100644",
                entry_object_id="blob_unchanged",
                entry_type="blob",
            ),
        ]

        database.create_index_entries(index_entries)
        database.sqlite.insert_many(tree_entries)

        # Add root tree entry
        database.sqlite.insert(
            TreeEntry(
                tree_id="",
                entry_name=".",
                entry_mode="040000",
                entry_object_id=tree_id,
                entry_type="tree",
            )
        )

        # Act
        index_entries = database.list_index_entries()
        tree = tree_store.build_commit_tree(sample_commit.tree_id)
        result = repository.entry_diff.diff(index_entries, tree.list_index_entries())

        # Assert
        assert result is not None
        assert result.is_empty() is False

        # Should have 1 added file
        assert len(result.added) == 1
        assert result.added[0].path == "./added_file.txt"

        # Should have 1 modified file
        assert len(result.modified) == 1
        assert result.modified[0].path == "./modified_file.txt"

        # Should have 1 deleted file (this will fail due to bug in original code)
        assert len(result.deleted) == 1

    def test_diff_with_changed_file_name(
        self, repository: Repository, database: Database, tree_store: TreeStore
    ):
        """Test diff with a combination of added, modified, and deleted files."""
        # Arrange
        repository.init()

        commit_datetime = datetime.datetime.now()
        sample_commit = Commit(
            tree_id="sample_tree_123",
            author_name="",
            author_email="",
            author_date=commit_datetime,
            committer_name="",
            committer_email="",
            message="Test commit",
            object_id="test_commit_123",
            committer_date=commit_datetime,
            created_at=commit_datetime,
            generation_number=0
        )

        database.sqlite.insert(sample_commit)
        tree_id = sample_commit.tree_id

        index_entries = [
            IndexEntry(
                path="./after.txt",
                object_id="blob_modified",
                mode="100644",
                size=200,
            ),
        ]

        tree_entries = [
            TreeEntry(
                tree_id=tree_id,
                entry_name="before.txt",
                entry_mode="100644",
                entry_object_id="blob_modified",
                entry_type="blob",
            ),
        ]

        database.create_index_entries(index_entries)
        database.sqlite.insert_many(tree_entries)

        # Add root tree entry
        database.sqlite.insert(
            TreeEntry(
                tree_id="",
                entry_name=".",
                entry_mode="040000",
                entry_object_id=tree_id,
                entry_type="tree",
            )
        )

        # Act
        index_entries = database.list_index_entries()
        tree = tree_store.build_commit_tree(sample_commit.tree_id)
        result = repository.entry_diff.diff(index_entries, tree.list_index_entries())

        # Assert
        assert result is not None
        assert result.is_empty() is False

        # Should have 1 added file
        assert len(result.added) == 1
        assert result.added[0].path == "./after.txt"

        # Should have 1 deleted file (this will fail due to bug in original code)
        assert len(result.deleted) == 1
        assert result.deleted[0].path == "./before.txt"

    def test_diff_with_nested_directory_structure(
        self, repository: Repository, database: Database, tree_store: TreeStore
    ):
        """Test diff with nested directory structure."""
        # Arrange
        repository.init()

        commit_datetime = datetime.datetime.now()
        sample_commit = Commit(
            tree_id="sample_tree_123",
            author_name="",
            author_email="",
            author_date=commit_datetime,
            committer_name="",
            committer_email="",
            message="Test commit",
            object_id="test_commit_123",
            committer_date=commit_datetime,
            created_at=commit_datetime,
            generation_number=0
        )

        database.sqlite.insert(sample_commit)
        tree_id = sample_commit.tree_id
        sub_tree_id = "sub_tree_123"

        # Add files to index with nested paths
        index_entries = [
            IndexEntry(
                path="./subdir/nested_file.txt",
                object_id="blob_nested_new",
                mode="100644",
                size=100,
            )
        ]

        # Create nested tree structure
        tree_entries = [
            # Root tree entry
            TreeEntry(
                tree_id=tree_id,
                entry_name="subdir",
                entry_mode="040000",
                entry_object_id=sub_tree_id,
                entry_type="tree",
            ),
            # Sub tree entry with different content
            TreeEntry(
                tree_id=sub_tree_id,
                entry_name="nested_file.txt",
                entry_mode="100644",
                entry_object_id="blob_nested_old",
                entry_type="blob",
            ),
        ]

        database.create_index_entries(index_entries)
        database.sqlite.insert_many(tree_entries)

        # Add root tree entry
        database.sqlite.insert(
            TreeEntry(
                tree_id="",
                entry_name=".",
                entry_mode="040000",
                entry_object_id=tree_id,
                entry_type="tree",
            )
        )

        # Act
        index_entries = database.list_index_entries()
        tree = tree_store.build_commit_tree(sample_commit.tree_id)
        result = repository.entry_diff.diff(index_entries, tree.list_index_entries())

        # Assert
        assert result is not None
        assert result.is_empty() is False
        assert len(result.added) == 0
        assert len(result.deleted) == 0
        assert len(result.modified) == 1
        assert result.modified[0].path == "./subdir/nested_file.txt"


class TestRepositoryCheckout:
    def test_checkout_branch(
        self,
        repository: Repository,
        test_file_path,
    ):
        repository.init()

        content = "Sample content"
        test_file_path.write_text(content)

        with patch("os.getcwd", return_value=test_file_path.parent.as_posix()):
            repository.add_index([test_file_path.name])
            test_file_entry = repository.index_store.find_by_paths(
                [test_file_path.name]
            )[0]

            first_commit = repository.commit("Initial commit")
            assert first_commit is not None

            # Create and checkout new branch
            new_branch_name = "new-branch"
            repository.create_branch(new_branch_name)
            result = repository.checkout(new_branch_name)
            assert result.success, f"Checkout failed: {result.error}"

            status_result = repository.status()
            assert status_result.success
            status = status_result.value
            assert status is not None
            assert status.branch_name == new_branch_name
            assert status.staged.is_empty()
            assert status.unstaged.is_empty()

            checkout_branch_entries = repository.database.list_index_entries()
            assert len(checkout_branch_entries) == 1
            assert checkout_branch_entries[0] == test_file_entry

            paths = repository.worktree.find_paths([test_file_path.name])
            assert len(paths) == 1
            path = paths[0]
            with open(path, "r") as f:
                file_content = f.read()
            assert file_content == content
            assert test_file_path.stat().st_mode == path.stat().st_mode

            # Modify file in new branch
            test_file_path.write_text("Modified content")

            repository.add_index([test_file_path.name])
            repository.commit("Modify file in new branch")

            modified_index_entries = repository.index_store.find_by_paths(
                [test_file_path.name]
            )

            paths = repository.worktree.find_paths([test_file_path.name])
            assert len(paths) == 1
            path = paths[0]
            with open(path, "r") as f:
                file_content = f.read()
            assert file_content == "Modified content"

            logs = repository.log()
            assert len(logs) == 2
            assert logs[0].message == "Modify file in new branch"
            assert logs[1].message == "Initial commit"

            # Checkout main branch and verify original content
            repository.checkout("main")

            paths = repository.worktree.find_paths([test_file_path.name])
            assert len(paths) == 1
            path = paths[0]
            with open(path, "r") as f:
                file_content = f.read()
            assert file_content == "Sample content"

            status_result = repository.status()
            assert status_result.success
            status = status_result.value
            assert status is not None
            assert status.branch_name == "main"
            assert status.staged.is_empty()
            assert status.unstaged.is_empty()

            logs = repository.log()
            assert len(logs) == 1
            assert logs[0].message == "Initial commit"

            # Add new file in main branch
            _, temp_path = tempfile.mkstemp(dir=test_file_path.parent)
            main_new_file = Path(temp_path)
            main_new_file.write_text("new file in main branch")
            repository.add_index([main_new_file.name])
            repository.commit("Add new file in main branch")

            logs = repository.log()
            assert len(logs) == 2
            assert logs[0].message == "Add new file in main branch"
            assert logs[1].message == "Initial commit"

            # Switch back to new branch and verify changes persist
            result = repository.checkout(new_branch_name)
            assert result.success, f"Checkout failed: {result.error}"

            status_result = repository.status()
            assert status_result.success
            status = status_result.value
            assert status is not None
            assert status.branch_name == new_branch_name
            assert status.staged.is_empty()
            assert status.unstaged.is_empty()

            checkout_branch_entries = repository.database.list_index_entries()
            assert len(checkout_branch_entries) == 1
            assert checkout_branch_entries[0] == modified_index_entries[0]

            paths = repository.worktree.find_paths([test_file_path.name])
            assert len(paths) == 1
            path = paths[0]
            with open(path, "r") as f:
                file_content = f.read()
            assert file_content == "Modified content"
            assert test_file_path.stat().st_mode == path.stat().st_mode

    def test_checkout_on_delete_file(
        self,
        repository: Repository,
        test_file_path,
    ):
        repository.init()

        content = "Sample content"
        test_file_path.write_text(content)

        with patch("os.getcwd", return_value=test_file_path.parent.as_posix()):
            repository.add_index([test_file_path.name])
            repository.commit("Initial commit")

            # Create and checkout new branch
            new_branch_name = "new-branch"
            repository.create_branch(new_branch_name)
            repository.checkout(new_branch_name)

            # Delete the file in the new branch
            test_file_path.unlink()
            repository.add_index([test_file_path.name])
            repository.commit("Delete file in new branch")

            assert test_file_path.parent.exists()

            # Verify file is deleted in new branch
            paths = repository.worktree.find_paths([test_file_path.name])
            assert len(paths) == 0

            # Checkout main branch and verify file is restored
            repository.checkout("main")

            paths = repository.worktree.find_paths([test_file_path.name])
            assert len(paths) == 1
            path = paths[0]
            with open(path, "r") as f:
                file_content = f.read()

            assert file_content == content
            assert path.stat().st_mode == test_file_path.stat().st_mode
            assert path.stat().st_size == test_file_path.stat().st_size

            # Checkout new branch again and verify file is deleted
            repository.checkout(new_branch_name)
            paths = repository.worktree.find_paths([test_file_path.name])
            assert len(paths) == 0
            assert not test_file_path.parent.exists()

            assert len(repository.database.list_index_entries()) == 0
            assert len(repository.log()) == 2

    def test_checkout_on_delete_parent_directory(
        self,
        repository: Repository,
        test_directory: Path,
    ):
        repository.init()

        # Create nested directory structure
        # sub_dir/sub_sub_dir/file.txt
        dir_level2 = test_directory / "sub_dir"
        dir_level2.mkdir()
        dir_level3 = dir_level2 / "sub_sub_dir"
        dir_level3.mkdir()
        file_path = dir_level3 / "file.txt"
        file_path.write_text("Sample content")

        with patch("os.getcwd", return_value=test_directory.as_posix()):
            repository.add_index([str(file_path.relative_to(test_directory))])
            repository.commit("Initial commit")

            # Create and checkout new branch
            new_branch_name = "new-branch"
            repository.create_branch(new_branch_name)
            repository.checkout(new_branch_name)

            # Delete the file.txt in sub_dir in the new branch
            file_path.unlink()
            repository.add_index([str(file_path.relative_to(test_directory))])
            repository.commit("Delete directory in new branch")

            assert dir_level3.exists()
            assert dir_level2.exists()
            assert test_directory.exists()

            # Verify directory is deleted in new branch
            paths = repository.worktree.find_paths(
                [str(dir_level3.relative_to(test_directory))]
            )
            assert len(paths) == 0

            # Checkout main branch and verify directory is restored
            repository.checkout("main")

            paths = repository.worktree.find_paths(
                [str(file_path.relative_to(test_directory))]
            )
            assert len(paths) == 1
            path = paths[0]
            with open(path, "r") as f:
                file_content = f.read()

            assert file_content == "Sample content"
            assert path.stat().st_mode == file_path.stat().st_mode
            assert path.stat().st_size == file_path.stat().st_size

            # Checkout new branch again and verify directory is deleted
            repository.checkout(new_branch_name)
            paths = repository.worktree.find_paths(
                [str(dir_level3.relative_to(test_directory))]
            )
            assert len(paths) == 0
            assert not dir_level3.exists()
            assert not dir_level2.exists()
            assert not test_directory.exists()

            assert len(repository.database.list_index_entries()) == 0

    def test_checkout_nonexistent_branch(
        self,
        repository: Repository,
    ):
        repository.init()

        result = repository.checkout("nonexistent-branch")
        assert not result.success
        assert result.error == "Branch 'refs/heads/nonexistent-branch' not found"

    def test_checkout_same_branch(
        self,
        repository: Repository,
        test_file_path,
    ):
        repository.init()

        content = "Sample content"
        test_file_path.write_text(content)

        with patch("os.getcwd", return_value=test_file_path.parent.as_posix()):
            repository.add_index([test_file_path.name])
            repository.commit("Initial commit")

            # Checkout the same branch 'main'
            result = repository.checkout("main")
            assert result.success

            head = repository.get_head_branch()
            assert head is not None
            assert head.branch_name == "main"

    def test_checkout_exist_uncommitted_changes(
        self,
        repository: Repository,
        test_file_path,
    ):
        repository.init()

        with patch("os.getcwd", return_value=test_file_path.parent.as_posix()):
            repository.add_index([test_file_path.name])
            repository.commit("Initial commit")

            _, temp_path = tempfile.mkstemp(dir=repository.worktree.root_dir)
            uncommitted_file = Path(temp_path)
            uncommitted_file.write_text("uncommitted changes")

            # Create and checkout new branch
            new_branch_name = "new-branch"
            result = repository.create_branch(new_branch_name)
            assert result.success

            status_result = repository.status()

            assert status_result.success
            status = status_result.value
            assert status is not None
            assert status.branch_name == "main"
            assert len(status.unstaged.added) == 1

            result = repository.checkout(new_branch_name)
            assert not result.success
            assert (
                result.error
                == "You have uncommitted changes. Please commit or stash them before checkout."
            )
