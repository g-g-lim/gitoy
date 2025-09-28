from database.database import Database

from database.entity.tree_entry import TreeEntry
from repository.repository import Repository
from repository.tree_store import TreeStore
from repository.tree import Tree

from test.util import check_parent_child_id


class TestTreeStoreBuildCommitTree:
    """Test cases for TreeStore.build_commit_tree method."""

    def test_build_commit_tree_with_empty_tree(
        self, tree_store: TreeStore, repository: Repository
    ):
        """Test building a commit tree with empty root tree."""
        # Arrange: Create root tree but no entries
        repository.init()
        root_tree_id = "root_tree_123"

        # Act
        result = tree_store.build_commit_tree(root_tree_id)

        # Assert
        assert result is not None
        assert result.root_entry is None

    def test_build_commit_tree_with_single_level_tree(
        self, tree_store: TreeStore, repository: Repository, database: Database
    ):
        """Test building a commit tree with single level (root only)."""
        # Arrange: Initialize database and create tree entries
        repository.init()
        root_tree_id = "root_tree_123"

        # Create tree entries in database
        tree_entries = [
            TreeEntry(
                tree_id=root_tree_id,
                entry_name="file1.txt",
                entry_mode="100644",
                entry_object_id="blob_1",
                entry_type="blob",
            ),
            TreeEntry(
                tree_id=root_tree_id,
                entry_name="file2.txt",
                entry_mode="100644",
                entry_object_id="blob_2",
                entry_type="blob",
            ),
        ]

        database.sqlite.insert_many(tree_entries)

        # Add the root tree entry itself
        database.sqlite.insert(
            TreeEntry(
                tree_id="",
                entry_name="root",
                entry_mode="040000",
                entry_object_id=root_tree_id,
                entry_type="tree",
            )
        )

        # Act
        result = tree_store.build_commit_tree(root_tree_id)

        # Assert
        assert result is not None
        assert isinstance(result, Tree)
        assert result.root_entry.entry_object_id == root_tree_id

    def test_build_commit_tree_with_nested_trees(
        self, tree_store: TreeStore, repository: Repository, database: Database
    ):
        """Test building a commit tree with nested directory structure."""
        # Arrange: Initialize database
        repository.init()
        root_tree_id = "root_tree_123"
        sub_tree_id = "sub_tree_456"

        # Create nested tree structure:
        # root/
        #   file1.txt (blob)
        #   subdir/ (tree)
        #     file2.txt (blob)

        # Root tree entries
        root_entries = [
            TreeEntry(
                tree_id=root_tree_id,
                entry_name="file1.txt",
                entry_mode="100644",
                entry_object_id="blob_1",
                entry_type="blob",
            ),
            TreeEntry(
                tree_id=root_tree_id,
                entry_name="subdir",
                entry_mode="040000",
                entry_object_id=sub_tree_id,
                entry_type="tree",
            ),
        ]

        # Sub tree entries
        sub_entries = [
            TreeEntry(
                tree_id=sub_tree_id,
                entry_name="file2.txt",
                entry_mode="100644",
                entry_object_id="blob_2",
                entry_type="blob",
            )
        ]

        # Insert all entries
        database.sqlite.insert_many(root_entries + sub_entries)

        # Add tree entries themselves
        database.sqlite.insert(
            TreeEntry(
                tree_id="",
                entry_name="root",
                entry_mode="040000",
                entry_object_id=root_tree_id,
                entry_type="tree",
            )
        )

        database.sqlite.insert(
            TreeEntry(
                tree_id="parent",
                entry_name="subdir",
                entry_mode="040000",
                entry_object_id=sub_tree_id,
                entry_type="tree",
            )
        )

        # Act
        result = tree_store.build_commit_tree(root_tree_id)

        # Assert
        assert result is not None
        assert isinstance(result, Tree)
        assert result.root_entry is not None
        assert result.root_entry.entry_object_id == root_tree_id

        # Check that the tree cache contains entries
        assert result.index.size == 4
        assert result.index.get("root") is not None
        assert result.index.get("root").entry_object_id == root_tree_id
        assert result.index.get("root/subdir") is not None
        assert result.index.get("root/subdir").entry_object_id == sub_tree_id
        assert result.index.get("root/subdir/file2.txt") is not None
        assert result.index.get("root/subdir/file2.txt").entry_object_id == "blob_2"
        assert result.index.get("root/file1.txt") is not None
        assert result.index.get("root/file1.txt").entry_object_id == "blob_1"

    def test_build_commit_tree_deeply_nested_structure(
        self, tree_store: TreeStore, repository: Repository, database: Database
    ):
        """Test building a deeply nested directory structure."""
        # Arrange: Create a 3-level deep structure
        repository.init()
        root_tree_id = "root_tree_123"
        level1_tree_id = "level1_tree_456"
        level2_tree_id = "level2_tree_789"

        # Structure:
        # root/
        #   level1/
        #     level2/
        #       deep_file.txt

        root_entries = [
            TreeEntry(
                tree_id=root_tree_id,
                entry_name="level1",
                entry_mode="040000",
                entry_object_id=level1_tree_id,
                entry_type="tree",
            )
        ]

        level1_entries = [
            TreeEntry(
                tree_id=level1_tree_id,
                entry_name="level2",
                entry_mode="040000",
                entry_object_id=level2_tree_id,
                entry_type="tree",
            )
        ]

        level2_entries = [
            TreeEntry(
                tree_id=level2_tree_id,
                entry_name="deep_file.txt",
                entry_mode="100644",
                entry_object_id="blob_deep",
                entry_type="blob",
            )
        ]

        # Insert all entries
        database.sqlite.insert_many(root_entries + level1_entries + level2_entries)

        # Add tree entries themselves
        database.sqlite.insert(
            TreeEntry(
                tree_id="",
                entry_name="root",
                entry_mode="040000",
                entry_object_id=root_tree_id,
                entry_type="tree",
            )
        )

        # Act
        result = tree_store.build_commit_tree(root_tree_id)

        # Assert
        assert result is not None
        assert isinstance(result, Tree)
        assert result.root_entry.entry_object_id == root_tree_id

        # Verify the nested structure was built
        assert result.index.size == 4
        assert result.index.get("root") is not None
        assert result.index.get("root/level1") is not None
        assert result.index.get("root/level1/level2") is not None
        assert result.index.get("root/level1/level2/deep_file.txt") is not None

    def test_build_commit_tree_duplicated_structure(
        self, tree_store: TreeStore, repository: Repository, database: Database
    ):
        """Test building a deeply duplicated directory structure."""
        # Arrange: Create a 3-level deep structure
        repository.init()
        root_tree_id = "root_tree_123"
        level1_tree_id = "level1_tree_456"
        level2_tree_id = "level2_tree_789"

        # Structure: level2 directory, file is duplicated
        # root/
        #   level1/
        #     level2/
        #       test.txt
        #   level2/
        #     test.txt

        root_entries = [
            TreeEntry(
                tree_id=root_tree_id,
                entry_name="level1",
                entry_mode="040000",
                entry_object_id=level1_tree_id,
                entry_type="tree",
            ),
            TreeEntry(
                tree_id=root_tree_id,
                entry_name="level2",
                entry_mode="040000",
                entry_object_id=level2_tree_id,
                entry_type="tree",
            ),
        ]

        level1_entries = [
            TreeEntry(
                tree_id=level1_tree_id,
                entry_name="level2",
                entry_mode="040000",
                entry_object_id=level2_tree_id,
                entry_type="tree",
            )
        ]

        level2_entries = [
            TreeEntry(
                tree_id=level2_tree_id,
                entry_name="test.txt",
                entry_mode="100644",
                entry_object_id="blob_deep",
                entry_type="blob",
            )
        ]

        # Insert all entries
        database.sqlite.insert_many(root_entries + level1_entries + level2_entries)

        # Add tree entries themselves
        database.sqlite.insert(
            TreeEntry(
                tree_id="",
                entry_name="root",
                entry_mode="040000",
                entry_object_id=root_tree_id,
                entry_type="tree",
            )
        )

        # Act
        result = tree_store.build_commit_tree(root_tree_id)

        # Assert
        assert result is not None
        assert isinstance(result, Tree)
        assert result.root_entry.entry_object_id == root_tree_id

        # Verify the nested structure was built
        assert result.index.size == 6
        assert result.index.get("root") is not None
        assert result.index.get("root/level1") is not None
        assert result.index.get("root/level1/level2") is not None
        assert result.index.get("root/level1/level2/test.txt") is not None
        assert result.index.get("root/level2") is not None
        assert result.index.get("root/level2/test.txt") is not None
        assert result.index.get("root/level1/level2/test.txt") is not result.index.get(
            "root/level2/test.txt"
        )


class TestTreeStoreSaveCommitTree:
    def test_save_commit_tree(
        self, tree_store: TreeStore, repository: Repository, database: Database
    ):
        # Given
        repository.init()
        root_tree_id = "root_tree_123"
        level1_tree_id = "level1_tree_456"
        level2_tree_id = "level2_tree_789"

        # Structure:
        # ./
        #   level1/
        #     level2/
        #       deep_file.txt

        root_entries = [
            TreeEntry(
                tree_id=root_tree_id,
                entry_name="level1",
                entry_mode="040000",
                entry_object_id=level1_tree_id,
                entry_type="tree",
            )
        ]

        level1_entries = [
            TreeEntry(
                tree_id=level1_tree_id,
                entry_name="level2",
                entry_mode="040000",
                entry_object_id=level2_tree_id,
                entry_type="tree",
            )
        ]

        level2_entries = [
            TreeEntry(
                tree_id=level2_tree_id,
                entry_name="deep_file.txt",
                entry_mode="100644",
                entry_object_id="blob_deep",
                entry_type="blob",
            )
        ]

        root_entry = TreeEntry(
            tree_id="",
            entry_name=".",
            entry_mode="040000",
            entry_object_id=root_tree_id,
            entry_type="tree",
        )

        # When
        tree_store.save_commit_tree(
            root_entry, root_entries + level1_entries + level2_entries
        )

        # Then
        tree = tree_store.build_commit_tree(root_tree_id)
        assert tree is not None
        assert tree.root_entry is not None
        check_parent_child_id(tree.root_entry)
        assert tree.get_entry("./level1").entry_object_id == level1_tree_id
        assert tree.get_entry("./level1/level2").entry_object_id == level2_tree_id
        assert (
            tree.get_entry("./level1/level2/deep_file.txt").entry_object_id
            == "blob_deep"
        )

    def test_save_commit_tree_with_duplicate_structure(
        self, tree_store: TreeStore, repository: Repository, database: Database
    ):
        # Given
        repository.init()
        root_tree_id = "root_tree_123"
        level1_tree_id = "level1_tree_456"
        level2_tree_id = "level2_tree_789"

        # Structure:
        # ./
        #   level1/
        #     level2/
        #       deep_file.txt
        #  level2/
        #    deep_file.txt

        root_entries = [
            TreeEntry(
                tree_id=root_tree_id,
                entry_name="level1",
                entry_mode="040000",
                entry_object_id=level1_tree_id,
                entry_type="tree",
            ),
            TreeEntry(
                tree_id=root_tree_id,
                entry_name="level2",
                entry_mode="040000",
                entry_object_id=level2_tree_id,
                entry_type="tree",
            ),
        ]

        level1_entries = [
            TreeEntry(
                tree_id=level1_tree_id,
                entry_name="level2",
                entry_mode="040000",
                entry_object_id=level2_tree_id,
                entry_type="tree",
            )
        ]

        level2_entries = [
            TreeEntry(
                tree_id=level2_tree_id,
                entry_name="deep_file.txt",
                entry_mode="100644",
                entry_object_id="blob_deep",
                entry_type="blob",
            )
        ]

        root_entry = TreeEntry(
            tree_id="",
            entry_name=".",
            entry_mode="040000",
            entry_object_id=root_tree_id,
            entry_type="tree",
        )

        # When
        tree_store.save_commit_tree(
            root_entry, root_entries + level1_entries + level2_entries
        )

        # Then
        tree = tree_store.build_commit_tree(root_tree_id)
        assert tree is not None
        assert tree.root_entry is not None
        assert len(database.sqlite.select("SELECT * FROM tree_entry")) == 5

        check_parent_child_id(tree.root_entry)

        assert tree.get_entry("./level1").entry_object_id == level1_tree_id
        assert tree.get_entry("./level1/level2").entry_object_id == level2_tree_id
        assert (
            tree.get_entry("./level1/level2/deep_file.txt").entry_object_id
            == "blob_deep"
        )
        assert tree.get_entry("./level2").entry_object_id == level2_tree_id
        assert tree.get_entry("./level2/deep_file.txt").entry_object_id == "blob_deep"

    def test_save_commit_tree_with_duplicate_structure_2(
        self, tree_store: TreeStore, repository: Repository, database: Database
    ):
        # Given
        repository.init()
        root_tree_id = "root_tree_123"
        level1_tree_id = "level1_tree_456"
        level2_tree_id = "level2_tree_789"
        level3_tree_id = "level3_tree"

        # Structure:
        # ./
        #   level1/
        #     level2/
        #       level3/
        #         deep_file.txt
        #  level2/
        #    level3/
        #      deep_file.txt

        root_entries = [
            TreeEntry(
                tree_id=root_tree_id,
                entry_name="level1",
                entry_mode="040000",
                entry_object_id=level1_tree_id,
                entry_type="tree",
            ),
            TreeEntry(
                tree_id=root_tree_id,
                entry_name="level2",
                entry_mode="040000",
                entry_object_id=level2_tree_id,
                entry_type="tree",
            ),
        ]

        level1_entries = [
            TreeEntry(
                tree_id=level1_tree_id,
                entry_name="level2",
                entry_mode="040000",
                entry_object_id=level2_tree_id,
                entry_type="tree",
            )
        ]

        level2_entries = [
            TreeEntry(
                tree_id=level2_tree_id,
                entry_name="level3",
                entry_mode="040000",
                entry_object_id=level3_tree_id,
                entry_type="tree",
            )
        ]

        level3_entries = [
            TreeEntry(
                tree_id=level3_tree_id,
                entry_name="deep_file.txt",
                entry_mode="100644",
                entry_object_id="blob_deep",
                entry_type="blob",
            )
        ]

        root_entry = TreeEntry(
            tree_id="",
            entry_name=".",
            entry_mode="040000",
            entry_object_id=root_tree_id,
            entry_type="tree",
        )

        # When
        tree_store.save_commit_tree(
            root_entry,
            root_entries + level1_entries + level2_entries + level3_entries,
        )

        # Then
        tree = tree_store.build_commit_tree(root_tree_id)
        assert tree is not None
        assert tree.root_entry is not None
        assert tree.entry_count == 8

        check_parent_child_id(tree.root_entry)

        assert tree.get_entry("./level1").entry_object_id == level1_tree_id
        assert tree.get_entry("./level1/level2").entry_object_id == level2_tree_id
        assert (
            tree.get_entry("./level1/level2/level3").entry_object_id == level3_tree_id
        )
        assert (
            tree.get_entry("./level1/level2/level3/deep_file.txt").entry_object_id
            == "blob_deep"
        )
        assert tree.get_entry("./level2").entry_object_id == level2_tree_id
        assert tree.get_entry("./level2/level3").entry_object_id == level3_tree_id
        assert (
            tree.get_entry("./level2/level3/deep_file.txt").entry_object_id
            == "blob_deep"
        )

        tree_entries_db = database.sqlite.select("SELECT * FROM tree_entry")
        assert len(tree_entries_db) == 6

    def test_save_commit_tree_on_already_exist_tree(
        self, tree_store: TreeStore, repository: Repository, database: Database
    ):
        # Given
        repository.init()
        root_tree_id = "root_tree_123"
        level1_tree_id = "level1_tree_456"
        level2_tree_id = "level2_tree_789"

        # Structure:
        # ./
        #   level1/
        #     level2/
        #       deep_file.txt

        root_entries = [
            TreeEntry(
                tree_id=root_tree_id,
                entry_name="level1",
                entry_mode="040000",
                entry_object_id=level1_tree_id,
                entry_type="tree",
            )
        ]

        level1_entries = [
            TreeEntry(
                tree_id=level1_tree_id,
                entry_name="level2",
                entry_mode="040000",
                entry_object_id=level2_tree_id,
                entry_type="tree",
            )
        ]

        level2_entries = [
            TreeEntry(
                tree_id=level2_tree_id,
                entry_name="deep_file.txt",
                entry_mode="100644",
                entry_object_id="blob_deep",
                entry_type="blob",
            )
        ]

        root_entry = TreeEntry(
            tree_id="",
            entry_name=".",
            entry_mode="040000",
            entry_object_id=root_tree_id,
            entry_type="tree",
        )

        # When
        tree_store.save_commit_tree(
            root_entry, root_entries + level1_entries + level2_entries
        )

        tree = tree_store.build_commit_tree(root_tree_id)
        assert tree is not None

        tree_store.save_commit_tree(
            root_entry, root_entries + level1_entries + level2_entries
        )

        # Then
        assert len(database.sqlite.select("SELECT * FROM tree_entry")) == 4
