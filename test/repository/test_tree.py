import hashlib
from database.entity.index_entry import IndexEntry
from repository.tree import Tree

from test.util import check_parent_child_id


class TestTreeAddUpdateDelete:
    """Test cases for Tree.add, delete, update method."""

    def test_tree_add(self):
        # Given
        tree = Tree()
        index_entry1 = IndexEntry(
            file_path="a/b/c.txt", object_id="dummy_oid1", file_mode="100644"
        )

        # When
        tree.add(index_entry1)

        # Then
        # Check if all intermediate and final entries are created
        assert tree.has_entry("a")
        assert tree.has_entry("a/b")
        assert tree.has_entry("a/b/c.txt")

        # Verify properties of each entry
        entry_a = tree.get_entry("a")
        assert entry_a.entry_name == "a"
        assert entry_a.entry_mode == "040000"
        assert entry_a.entry_type == "tree"
        assert entry_a.entry_object_id is None

        entry_b = tree.get_entry("a/b")
        assert entry_b.entry_name == "b"
        assert entry_b.entry_mode == "040000"
        assert entry_b.entry_type == "tree"
        assert entry_b.entry_object_id is None

        entry_c = tree.get_entry("a/b/c.txt")
        assert entry_c.entry_name == "c.txt"
        assert entry_c.entry_mode == "100644"
        assert entry_c.entry_type == "blob"
        assert entry_c.entry_object_id == "dummy_oid1"

        # Verify parent-child relationships
        assert len(entry_a.children) == 1
        assert entry_b in entry_a.children

        assert len(entry_b.children) == 1
        assert entry_c in entry_b.children

        # Given: Add another file to an existing directory
        index_entry2 = IndexEntry(
            file_path="a/b/d.txt", object_id="dummy_oid2", file_mode="100644"
        )

        # When
        tree.add(index_entry2)

        # Then
        assert tree.has_entry("a/b/d.txt")
        entry_d = tree.get_entry("a/b/d.txt")
        assert entry_d.entry_name == "d.txt"
        assert entry_d.entry_mode == "100644"
        assert entry_d.entry_type == "blob"
        assert entry_d.entry_object_id == "dummy_oid2"

        # Check that 'a/b' now has two children
        assert len(entry_b.children) == 2
        assert entry_c in entry_b.children
        assert entry_d in entry_b.children

    def test_tree_remove(self):
        # Scenario 1: Removing a file makes parent directories empty, so they should be pruned.
        # Given
        tree = Tree()
        index_entry1 = IndexEntry(
            file_path="./a/b/c.txt", object_id="dummy_oid1", file_mode="100644"
        )
        tree.add(index_entry1)

        # Sanity check
        assert tree.has_entry("./a/b/c.txt")
        assert tree.has_entry("./a/b")
        assert tree.has_entry("./a")
        assert tree.has_entry(".")

        # When
        tree.remove(index_entry1)

        # Then
        assert not tree.has_entry("./a/b/c.txt")
        assert not tree.has_entry("./a/b")
        assert not tree.has_entry("./a")
        assert tree.has_entry(".")

        # Scenario 2: Removing a file from a directory with other files.
        # The parent directory should NOT be pruned, but its object_id should be invalidated.
        # Given
        tree = Tree()
        index_entry2 = IndexEntry(
            file_path="./a/b/c.txt", object_id="dummy_oid1", file_mode="100644"
        )
        index_entry3 = IndexEntry(
            file_path="./a/d.txt", object_id="dummy_oid2", file_mode="100644"
        )
        tree.add(index_entry2)
        tree.add(index_entry3)

        # Simulate a committed state by giving object_ids to tree entries
        entry_a = tree.get_entry("./a")
        entry_a.entry_object_id = "dummy_oid_a"
        entry_b = tree.get_entry("./a/b")
        entry_b.entry_object_id = "dummy_oid_b"

        # When
        tree.remove(index_entry2)

        # Then
        # Check that the file is removed, but the other file and its parent remain
        assert not tree.has_entry("./a/b/c.txt")
        assert not tree.has_entry("./a/b")  # 'a/b' should be pruned as it's now empty
        assert tree.has_entry("./a/d.txt")
        assert tree.has_entry("./a")
        assert tree.has_entry(".")

        # Check that the object_id of the modified parent tree 'a' is set to None
        assert entry_a.entry_object_id is None

        # Check that the un-touched entry is still a child of 'a'
        entry_d = tree.get_entry("./a/d.txt")
        assert entry_d in entry_a.children

    def test_tree_update(self):
        # Given
        tree = Tree()
        initial_entry = IndexEntry(
            file_path="./a/b/c.txt", object_id="old_oid", file_mode="100644"
        )
        tree.add(initial_entry)

        # Simulate a committed state
        entry_root = tree.get_entry(".")
        entry_root.entry_object_id = "oid_root"
        entry_a = tree.get_entry("./a")
        entry_a.entry_object_id = "oid_a"
        entry_b = tree.get_entry("./a/b")
        entry_b.entry_object_id = "oid_b"
        entry_c = tree.get_entry("./a/b/c.txt")
        assert entry_c.entry_object_id == "old_oid"

        # When
        updated_entry = IndexEntry(
            file_path="./a/b/c.txt", object_id="new_oid", file_mode="100755"
        )
        tree.update(updated_entry)

        # Then
        # Check that the blob entry is updated
        assert entry_c.entry_object_id == "new_oid"
        assert entry_c.entry_mode == "100755"

        # Check that parent tree object_ids are invalidated
        assert entry_root.entry_object_id is None
        assert entry_a.entry_object_id is None
        assert entry_b.entry_object_id is None

    def test_tree_update_renamed_directory(self):
        # Given
        tree = Tree()
        original_entry = IndexEntry(
            file_path="./a/file.txt", object_id="same_oid", file_mode="100644"
        )
        tree.add(original_entry)
        assert tree.has_entry("./a/file.txt")

        # When
        renamed_entry = IndexEntry(
            file_path="./b/file.txt", object_id="same_oid", file_mode="100644"
        )
        tree.remove(original_entry)
        tree.add(renamed_entry)

        # Then
        # Verify the old path is removed
        assert not tree.has_entry("./a/file.txt")
        assert not tree.has_entry("./a")  # The parent 'a' should be pruned

        # Verify the new path exists
        assert tree.has_entry("./b/file.txt")
        assert tree.has_entry("./b")

        # Verify the new entry has the same object_id
        new_entry = tree.get_entry("./b/file.txt")
        assert new_entry.entry_name == "file.txt"
        assert new_entry.entry_object_id == "same_oid"


class TestTreeBuildObjectIds:
    def test_add_files_with_empty_tree(self):
        # Given
        tree = Tree()
        entry_c = IndexEntry(
            file_path="./a/b/c.txt", object_id="oid_c", file_mode="100644"
        )
        entry_d = IndexEntry(
            file_path="./a/d.txt", object_id="oid_d", file_mode="100644"
        )
        tree.add(entry_c)
        tree.add(entry_d)

        tree_b = tree.get_entry("./a/b")
        blob_c = tree.get_entry("./a/b/c.txt")
        content_b = blob_c.hashable_str
        expected_hash_b = hashlib.sha1(content_b.encode()).hexdigest()

        blob_d = tree.get_entry("./a/d.txt")
        tree_b.entry_object_id = expected_hash_b
        content_a = f"{tree_b.hashable_str}\n{blob_d.hashable_str}"
        expected_hash_a = hashlib.sha1(content_a.encode()).hexdigest()

        tree_b.entry_object_id = None

        tree_a = tree.get_entry("./a")
        tree_a.entry_object_id = expected_hash_a
        content_root = f"{tree_a.hashable_str}"
        expected_hash_root = hashlib.sha1(content_root.encode()).hexdigest()

        tree_a.entry_object_id = None

        # When
        result = tree.build_object_ids()

        # Then
        assert tree_b.entry_object_id == expected_hash_b
        assert tree.get_entry("./a").entry_object_id == expected_hash_a
        assert tree.get_entry(".").entry_object_id == expected_hash_root

        assert len(result) == 5
        assert sorted(result, key=lambda x: x.entry_name) == [
            tree.get_entry("."),
            tree_a,
            tree_b,
            blob_c,
            blob_d,
        ]

    def test_add_after_add(self):
        # Given
        tree = Tree()
        entry_c = IndexEntry(
            file_path="./a/b/c.txt", object_id="oid_c", file_mode="100644"
        )
        entry_d = IndexEntry(
            file_path="./a/d.txt", object_id="oid_d", file_mode="100644"
        )
        tree.add(entry_c)
        tree.add(entry_d)

        tree.build_object_ids()

        before_root_entry_id = tree.get_entry(".").entry_object_id
        before_tree_a_id = tree.get_entry("./a").entry_object_id
        before_tree_b_id = tree.get_entry("./a/b").entry_object_id

        entry_e = IndexEntry(
            file_path="./a/b/e.txt", object_id="oid_e", file_mode="100644"
        )

        tree.add(entry_e)

        tree_b = tree.get_entry("./a/b")
        blob_c = tree.get_entry("./a/b/c.txt")
        blob_e = tree.get_entry("./a/b/e.txt")
        content_b = blob_c.hashable_str + "\n" + blob_e.hashable_str
        expected_hash_b = hashlib.sha1(content_b.encode()).hexdigest()

        blob_d = tree.get_entry("./a/d.txt")
        tree_b.entry_object_id = expected_hash_b
        content_a = f"{tree_b.hashable_str}\n{blob_d.hashable_str}"
        expected_hash_a = hashlib.sha1(content_a.encode()).hexdigest()

        tree_b.entry_object_id = None

        tree_a = tree.get_entry("./a")
        tree_a.entry_object_id = expected_hash_a
        content_root = f"{tree_a.hashable_str}"
        expected_hash_root = hashlib.sha1(content_root.encode()).hexdigest()

        tree_a.entry_object_id = None

        # When
        result = tree.build_object_ids()

        # Then
        assert len(result) == 6
        assert sorted(result, key=lambda x: x.entry_name) == [
            tree.get_entry("."),
            tree_a,
            tree_b,
            blob_c,
            blob_d,
            blob_e,
        ]

        assert tree.get_entry("./a/b").entry_object_id == expected_hash_b
        assert tree.get_entry("./a").entry_object_id == expected_hash_a
        assert tree.get_entry(".").entry_object_id == expected_hash_root
        assert tree.get_entry("./a").entry_object_id != before_tree_a_id
        assert tree.get_entry("./a/b").entry_object_id != before_tree_b_id
        assert tree.get_entry(".").entry_object_id != before_root_entry_id

    def test_remove(self):
        # Given
        tree = Tree()
        entry_c = IndexEntry(
            file_path="./a/b/c.txt", object_id="oid_c", file_mode="100644"
        )
        entry_d = IndexEntry(
            file_path="./a/d.txt", object_id="oid_d", file_mode="100644"
        )
        tree.add(entry_c)
        tree.add(entry_d)

        tree.build_object_ids()

        before_root_entry_id = tree.get_entry(".").entry_object_id
        before_tree_a_id = tree.get_entry("./a").entry_object_id

        tree.remove(entry_c)

        blob_d = tree.get_entry("./a/d.txt")
        content_a = blob_d.hashable_str
        expected_hash_a = hashlib.sha1(content_a.encode()).hexdigest()

        tree_a = tree.get_entry("./a")
        tree_a.entry_object_id = expected_hash_a
        content_root = f"{tree_a.hashable_str}"
        expected_hash_root = hashlib.sha1(content_root.encode()).hexdigest()

        tree_a.entry_object_id = None

        # When
        result = tree.build_object_ids()

        # Then
        assert tree.get_entry("./a").entry_object_id == expected_hash_a
        assert tree.get_entry(".").entry_object_id == expected_hash_root
        assert tree.get_entry("./a").entry_object_id != before_tree_a_id
        assert tree.get_entry(".").entry_object_id != before_root_entry_id

        assert len(result) == 3
        assert sorted(result, key=lambda x: x.entry_name) == [
            tree.get_entry("."),
            tree_a,
            blob_d,
        ]

    def test_update(self):
        tree = Tree()
        entry_c = IndexEntry(
            file_path="./a/b/c.txt", object_id="oid_c", file_mode="100644"
        )
        entry_d = IndexEntry(
            file_path="./a/d.txt", object_id="oid_d", file_mode="100644"
        )
        tree.add(entry_c)
        tree.add(entry_d)

        tree.build_object_ids()

        before_root_entry_id = tree.get_entry(".").entry_object_id
        before_tree_a_id = tree.get_entry("./a").entry_object_id
        before_tree_b_id = tree.get_entry("./a/b").entry_object_id

        new_entry_c = IndexEntry(
            file_path="./a/b/c.txt", object_id="new_oid_c", file_mode="100644"
        )

        tree.update(new_entry_c)

        tree_b = tree.get_entry("./a/b")
        blob_c = tree.get_entry("./a/b/c.txt")
        content_b = blob_c.hashable_str
        expected_hash_b = hashlib.sha1(content_b.encode()).hexdigest()

        blob_d = tree.get_entry("./a/d.txt")
        tree_b.entry_object_id = expected_hash_b
        content_a = f"{tree_b.hashable_str}\n{blob_d.hashable_str}"
        expected_hash_a = hashlib.sha1(content_a.encode()).hexdigest()

        tree_b.entry_object_id = None

        tree_a = tree.get_entry("./a")
        tree_a.entry_object_id = expected_hash_a
        content_root = f"{tree_a.hashable_str}"
        expected_hash_root = hashlib.sha1(content_root.encode()).hexdigest()

        tree_a.entry_object_id = None

        # When
        result = tree.build_object_ids()

        # Then
        assert tree.get_entry("./a/b").entry_object_id == expected_hash_b
        assert tree.get_entry("./a").entry_object_id == expected_hash_a
        assert tree.get_entry(".").entry_object_id == expected_hash_root
        assert tree.get_entry("./a").entry_object_id != before_tree_a_id
        assert tree.get_entry("./a/b").entry_object_id != before_tree_b_id
        assert tree.get_entry(".").entry_object_id != before_root_entry_id

        assert len(result) == 5
        assert sorted(result, key=lambda x: x.entry_name) == [
            tree.get_entry("."),
            tree_a,
            tree_b,
            blob_c,
            blob_d,
        ]

    def test_update_duplicate_structure(self):
        # Given
        tree = Tree()
        entry_abc = IndexEntry(
            file_path="./a/b/c.txt", object_id="oid_c", file_mode="100644"
        )
        tree.add(entry_abc)

        tree.build_object_ids()

        entry_bc = IndexEntry(
            file_path="./b/c.txt", object_id="oid_c", file_mode="100644"
        )
        tree.add(entry_bc)

        # When
        result = tree.build_object_ids()

        # Then
        assert len(result) == 4
        assert sorted(result, key=lambda x: x.entry_name) == [
            tree.get_entry("."),
            tree.get_entry("./a"),
            tree.get_entry("./b"),
            tree.get_entry("./b/c.txt"),
        ]

    def test_check_tree_entry_ids(self):
        # Given
        tree = Tree()
        entry_abc = IndexEntry(
            file_path="./a/b/c.txt", object_id="oid_c", file_mode="100644"
        )
        entry_abd = IndexEntry(
            file_path="./a/b/d.txt", object_id="oid_d", file_mode="100644"
        )

        tree.add(entry_abc)
        tree.add(entry_abd)

        tree.build_object_ids()

        entry_ac = IndexEntry(
            file_path="./a/c.txt", object_id="oid_c", file_mode="100644"
        )

        tree.add(entry_ac)

        # When
        result = tree.build_object_ids()

        # Then
        assert len(result) == 4
        assert sorted(result, key=lambda x: x.entry_name) == [
            tree.get_entry("."),
            tree.get_entry("./a"),
            tree.get_entry("./a/b"),
            tree.get_entry("./a/c.txt"),
        ]

        assert tree.root_entry is not None
        check_parent_child_id(tree.root_entry)

    def test_tree_id_consistency_when_add(self):
        # Given
        tree = Tree()
        entry_ab = IndexEntry(
            file_path="./a/b.txt", object_id="oid_b", file_mode="100644"
        )
        tree.add(entry_ab)

        tree.build_object_ids()
        assert tree.root_entry is not None
        one_entry_id = tree.root_entry.entry_object_id

        tree = Tree()
        tree.add(entry_ab)

        tree.build_object_ids()

        assert tree.root_entry is not None
        other_entry_id = tree.root_entry.entry_object_id
        assert one_entry_id == other_entry_id

    def test_tree_id_consistency_when_update(self):
        # Given
        tree = Tree()
        entry_ab = IndexEntry(
            file_path="./a/b.txt", object_id="oid_b", file_mode="100644"
        )
        tree.add(entry_ab)
        update_entry_ab = IndexEntry(
            file_path="./a/b.txt", object_id="oid_bcdef", file_mode="100644"
        )
        tree.update(update_entry_ab)

        tree.build_object_ids()
        assert tree.root_entry is not None
        one_entry_id = tree.root_entry.entry_object_id

        tree = Tree()
        tree.add(entry_ab)
        tree.update(update_entry_ab)

        tree.build_object_ids()

        assert tree.root_entry is not None
        other_entry_id = tree.root_entry.entry_object_id
        assert one_entry_id == other_entry_id

    def test_tree_id_consistency_after_update_on_same_tree(self):
        # Given
        tree = Tree()
        entry_ab = IndexEntry(
            file_path="./a/b.txt", object_id="oid_b", file_mode="100644"
        )
        tree.add(entry_ab)
        tree.remove(entry_ab)

        tree.build_object_ids()
        assert tree.root_entry is not None
        before_entry_id = tree.root_entry.entry_object_id

        tree.add(entry_ab)
        tree.remove(entry_ab)

        tree.build_object_ids()

        assert tree.root_entry is not None
        after_entry_id = tree.root_entry.entry_object_id
        assert before_entry_id == after_entry_id
