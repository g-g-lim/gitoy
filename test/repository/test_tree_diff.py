"""
Test suite for TreeDiff class.

Tests the diff method including detection of added, modified,
and deleted files between index and commit tree.
"""

import datetime
import pytest
from database.database import Database
from database.entity.commit import Commit
from database.entity.index_entry import IndexEntry
from database.entity.tree_entry import TreeEntry
from repository.tree_diff import TreeDiff


@pytest.fixture
def sample_commit():
    """Create a sample commit for testing."""
    return Commit(
        tree_id="sample_tree_123",
        committer_name="Test Committer",
        committer_email="test@example.com",
        message="Test commit",
        object_id="test_commit_123",
        committer_date=datetime.datetime.now(),
        created_at=datetime.datetime.now(),
    )


class TestTreeDiff:
    """Test cases for TreeDiff class."""

    def test_diff_with_empty_index_and_empty_tree(
        self, tree_diff: TreeDiff, sample_commit: Commit, repository
    ):
        """Test diff with empty index and empty commit tree."""
        # Arrange
        repository.init()

        # Act
        result = tree_diff.diff(sample_commit)

        # Assert
        assert result is not None
        assert result.is_empty() is True
        assert len(result.added) == 0
        assert len(result.deleted) == 0
        assert len(result.modified) == 0

    def test_diff_with_files_added_to_index(
        self, tree_diff: TreeDiff, sample_commit: Commit, database: Database, repository
    ):
        # Arrange
        repository.init()

        # Add files to index
        index_entries = [
            IndexEntry(
                file_path="new_file1.txt",
                object_id="blob_123",
                file_mode="100644",
                file_size=100,
                ctime=1640995200.0,
                mtime=1640995200.0,
                dev=1,
                inode=12345,
                uid=1000,
                gid=1000,
                stage=0,
                assume_valid=False,
                skip_worktree=False,
                intent_to_add=False,
            ),
            IndexEntry(
                file_path="new_file2.txt",
                object_id="blob_456",
                file_mode="100644",
                file_size=200,
                ctime=1640995200.0,
                mtime=1640995200.0,
                dev=1,
                inode=12346,
                uid=1000,
                gid=1000,
                stage=0,
                assume_valid=False,
                skip_worktree=False,
                intent_to_add=False,
            ),
        ]

        database.create_index_entries(index_entries)

        # Act
        result = tree_diff.diff(sample_commit)

        # Assert
        assert result is not None
        assert result.is_empty() is False
        assert len(result.added) == 2
        assert len(result.deleted) == 0
        assert len(result.modified) == 0

        added_paths = [entry.file_path for entry in result.added]
        assert "new_file1.txt" in added_paths
        assert "new_file2.txt" in added_paths

    def test_diff_with_files_deleted_from_index(
        self, tree_diff: TreeDiff, sample_commit: Commit, database: Database, repository
    ):
        """Test diff when files exist in commit tree but not in index."""
        # Arrange
        repository.init()
        database.sqlite.insert(sample_commit)
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

        database.sqlite.insert_many(tree_entries)

        # Add root tree entry
        database.sqlite.insert(
            TreeEntry(
                tree_id="",
                entry_name="root",
                entry_mode="040000",
                entry_object_id=tree_id,
                entry_type="tree",
            )
        )

        # Act
        result = tree_diff.diff(sample_commit)

        # Assert - Note: This test will initially fail due to bug in original code
        assert result is not None
        assert result.is_empty() is False
        assert len(result.added) == 0
        assert len(result.deleted) == 2
        assert len(result.modified) == 0

    def test_diff_with_modified_files(
        self, tree_diff: TreeDiff, sample_commit: Commit, database: Database, repository
    ):
        """Test diff when files are modified (different object_id or mode)."""
        # Arrange
        repository.init()
        database.sqlite.insert(sample_commit)
        tree_id = sample_commit.tree_id

        # Add files to index
        index_entries = [
            IndexEntry(
                file_path="root/modified_file1.txt",
                object_id="blob_new_123",  # Different object_id
                file_mode="100644",
                file_size=100,
                ctime=1640995200.0,
                mtime=1640995200.0,
                dev=1,
                inode=12345,
                uid=1000,
                gid=1000,
                stage=0,
                assume_valid=False,
                skip_worktree=False,
                intent_to_add=False,
            ),
            IndexEntry(
                file_path="root/modified_file2.txt",
                object_id="blob_456",
                file_mode="100755",  # Different file_mode
                file_size=200,
                ctime=1640995200.0,
                mtime=1640995200.0,
                dev=1,
                inode=12346,
                uid=1000,
                gid=1000,
                stage=0,
                assume_valid=False,
                skip_worktree=False,
                intent_to_add=False,
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
                entry_name="root",
                entry_mode="040000",
                entry_object_id=tree_id,
                entry_type="tree",
            )
        )

        # Act
        result = tree_diff.diff(sample_commit)

        # Assert
        assert result is not None
        assert result.is_empty() is False
        assert len(result.added) == 0
        assert len(result.deleted) == 0
        assert len(result.modified) == 2

        modified_paths = [entry.file_path for entry in result.modified]
        assert "root/modified_file1.txt" in modified_paths
        assert "root/modified_file2.txt" in modified_paths

    def test_diff_with_unchanged_files(
        self, tree_diff: TreeDiff, sample_commit: Commit, database: Database, repository
    ):
        """Test diff when files are unchanged between index and commit."""
        # Arrange
        repository.init()
        database.sqlite.insert(sample_commit)
        tree_id = sample_commit.tree_id

        # Add files to index
        index_entries = [
            IndexEntry(
                file_path="root/unchanged_file.txt",
                object_id="blob_same",
                file_mode="100644",
                file_size=100,
                ctime=1640995200.0,
                mtime=1640995200.0,
                dev=1,
                inode=12345,
                uid=1000,
                gid=1000,
                stage=0,
                assume_valid=False,
                skip_worktree=False,
                intent_to_add=False,
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
                entry_name="root",
                entry_mode="040000",
                entry_object_id=tree_id,
                entry_type="tree",
            )
        )

        # Act
        result = tree_diff.diff(sample_commit)

        # Assert
        assert result is not None
        assert result.is_empty() is True
        assert len(result.added) == 0
        assert len(result.deleted) == 0
        assert len(result.modified) == 0

    def test_diff_with_mixed_changes(
        self, tree_diff: TreeDiff, sample_commit: Commit, database: Database, repository
    ):
        """Test diff with a combination of added, modified, and deleted files."""
        # Arrange
        repository.init()
        database.sqlite.insert(sample_commit)
        tree_id = sample_commit.tree_id

        # Files in index: added + modified + unchanged
        index_entries = [
            # Added file (not in tree)
            IndexEntry(
                file_path="root/added_file.txt",
                object_id="blob_added",
                file_mode="100644",
                file_size=100,
                ctime=1640995200.0,
                mtime=1640995200.0,
                dev=1,
                inode=12345,
                uid=1000,
                gid=1000,
                stage=0,
                assume_valid=False,
                skip_worktree=False,
                intent_to_add=False,
            ),
            # Modified file (different content)
            IndexEntry(
                file_path="root/modified_file.txt",
                object_id="blob_modified_new",
                file_mode="100644",
                file_size=200,
                ctime=1640995200.0,
                mtime=1640995200.0,
                dev=1,
                inode=12346,
                uid=1000,
                gid=1000,
                stage=0,
                assume_valid=False,
                skip_worktree=False,
                intent_to_add=False,
            ),
            # Unchanged file
            IndexEntry(
                file_path="root/unchanged_file.txt",
                object_id="blob_unchanged",
                file_mode="100644",
                file_size=300,
                ctime=1640995200.0,
                mtime=1640995200.0,
                dev=1,
                inode=12347,
                uid=1000,
                gid=1000,
                stage=0,
                assume_valid=False,
                skip_worktree=False,
                intent_to_add=False,
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
                entry_name="root",
                entry_mode="040000",
                entry_object_id=tree_id,
                entry_type="tree",
            )
        )

        # Act
        result = tree_diff.diff(sample_commit)

        # Assert
        assert result is not None
        assert result.is_empty() is False

        # Should have 1 added file
        assert len(result.added) == 1
        assert result.added[0].file_path == "root/added_file.txt"

        # Should have 1 modified file
        assert len(result.modified) == 1
        assert result.modified[0].file_path == "root/modified_file.txt"

        # Should have 1 deleted file (this will fail due to bug in original code)
        assert len(result.deleted) == 1

    def test_diff_with_changed_file_name(
        self, tree_diff: TreeDiff, sample_commit: Commit, database: Database, repository
    ):
        """Test diff with a combination of added, modified, and deleted files."""
        # Arrange
        repository.init()
        database.sqlite.insert(sample_commit)
        tree_id = sample_commit.tree_id

        index_entries = [
            IndexEntry(
                file_path="root/after.txt",
                object_id="blob_modified",
                file_mode="100644",
                file_size=200,
                ctime=1640995200.0,
                mtime=1640995200.0,
                dev=1,
                inode=12346,
                uid=1000,
                gid=1000,
                stage=0,
                assume_valid=False,
                skip_worktree=False,
                intent_to_add=False,
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
                entry_name="root",
                entry_mode="040000",
                entry_object_id=tree_id,
                entry_type="tree",
            )
        )

        # Act
        result = tree_diff.diff(sample_commit)

        # Assert
        assert result is not None
        assert result.is_empty() is False

        # Should have 1 added file
        assert len(result.added) == 1
        assert result.added[0].file_path == "root/after.txt"

        # Should have 1 deleted file (this will fail due to bug in original code)
        assert len(result.deleted) == 1
        assert result.deleted[0].file_path == "root/before.txt"

    def test_diff_with_nested_directory_structure(
        self, tree_diff: TreeDiff, sample_commit: Commit, database: Database, repository
    ):
        """Test diff with nested directory structure."""
        # Arrange
        repository.init()
        database.sqlite.insert(sample_commit)
        tree_id = sample_commit.tree_id
        sub_tree_id = "sub_tree_123"

        # Add files to index with nested paths
        index_entries = [
            IndexEntry(
                file_path="root/subdir/nested_file.txt",
                object_id="blob_nested_new",
                file_mode="100644",
                file_size=100,
                ctime=1640995200.0,
                mtime=1640995200.0,
                dev=1,
                inode=12345,
                uid=1000,
                gid=1000,
                stage=0,
                assume_valid=False,
                skip_worktree=False,
                intent_to_add=False,
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
                entry_name="root",
                entry_mode="040000",
                entry_object_id=tree_id,
                entry_type="tree",
            )
        )

        # Act
        result = tree_diff.diff(sample_commit)

        # Assert
        assert result is not None
        assert result.is_empty() is False
        assert len(result.added) == 0
        assert len(result.deleted) == 0
        assert len(result.modified) == 1
        assert result.modified[0].file_path == "root/subdir/nested_file.txt"
