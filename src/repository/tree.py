import hashlib
from typing import Optional
from database.entity.index_entry import IndexEntry
from database.entity.tree_entry import TreeEntry
from util.path import accumulate_paths


class TreeIndex:
    def __init__(self):
        self.cache: dict[str, TreeEntry] = {}

    def get(self, path) -> Optional[TreeEntry]:
        return self.cache.get(path)

    def set(self, path, tree):
        self.cache[path] = tree

    def remove(self, path):
        if path in self.cache:
            del self.cache[path]

    def __iter__(self):
        for key in self.cache.keys():
            yield (key, self.cache[key])

    @property
    def size(self):
        return len(self.cache)


class Tree:
    def __init__(self, root_tree: Optional[TreeEntry] = None):
        self.root_entry = root_tree
        self.index = TreeIndex()

    def get_entry(self, path):
        return self.index.get(path)

    def has_entry(self, path):
        return self.get_entry(path) is not None
    
    def list_index_entries(self) -> list[IndexEntry]:
        return [
            IndexEntry(
            file_path=path,
            file_mode=entry.entry_mode,
            object_id=entry.entry_object_id) 
            for path, entry in self.index if entry.entry_object_id is not None and entry.entry_type == "blob"
        ]

    @property
    def entry_count(self):
        return self.index.size

    def add(self, index_entry: IndexEntry):
        paths = accumulate_paths(index_entry.file_path)
        parent_tree_entry: Optional[TreeEntry] = None
        for path in paths:
            tree_entry = self.index.get(path)
            if tree_entry is None:
                entry_name = path.split("/")[-1]
                entry_type = "blob" if path == paths[-1] else "tree"
                entry_mode = index_entry.file_mode if entry_type == "blob" else "040000"
                entry_object_id = (
                    index_entry.object_id if entry_type == "blob" else None
                )
                tree_entry = TreeEntry(
                    entry_name, entry_mode, entry_type, entry_object_id
                )
                if parent_tree_entry:
                    parent_tree_entry.append_child(tree_entry)
                self.index.set(path, tree_entry)
                if self.root_entry is None and tree_entry.entry_name == ".":
                    self.root_entry = tree_entry
            else:
                # invalidate object_jd
                tree_entry.entry_object_id = None
            if tree_entry.entry_type == "tree":
                parent_tree_entry = tree_entry

    def remove(self, index_entry: IndexEntry):
        paths = accumulate_paths(index_entry.file_path)
        parent_tree_entry: Optional[TreeEntry] = None

        # remove target blob tree
        for path in paths:
            tree_entry = self.index.get(path)
            if tree_entry is None:
                raise KeyError(
                    f"Mismatch for path '{path}' when removing entry from tree"
                )
            tree_entry.relative_path = path
            if parent_tree_entry is not None and tree_entry.entry_type == "blob":
                self.index.remove(tree_entry.relative_path)
                parent_tree_entry.remove_child(tree_entry)
            else:
                # invalidate object_jd
                tree_entry.entry_object_id = None
                parent_tree_entry = tree_entry

        # remove tree entry with empty children
        while parent_tree_entry and len(parent_tree_entry.children) == 0:
            parent_parent = parent_tree_entry.parent
            if parent_parent is None:
                break
            parent_parent.remove_child(parent_tree_entry)
            self.index.remove(parent_tree_entry.relative_path)
            parent_tree_entry = parent_parent

    def update(self, index_entry: IndexEntry):
        paths = accumulate_paths(index_entry.file_path)
        for path in paths:
            tree_entry = self.index.get(path)
            if tree_entry is None:
                raise KeyError(
                    f"Mismatch for path '{path}' when modifying entry from tree"
                )
            if tree_entry.entry_type == "blob":
                tree_entry.entry_object_id = index_entry.object_id
                tree_entry.entry_mode = index_entry.file_mode
            else:
                # invalidate object_jd
                tree_entry.entry_object_id = None

    def build_object_ids(self):
        updated_entries = []

        def _hash_tree_entry(tree_entry: TreeEntry):
            for child in tree_entry.children:
                if child.entry_type == "tree" and child.entry_object_id is None:
                    _hash_tree_entry(child)

            sorted_children = sorted(tree_entry.children, key=lambda x: x.entry_name)
            content = "\n".join(child.hashable_str for child in sorted_children)
            sha1 = hashlib.sha1()
            sha1.update(content.encode())
            tree_entry.entry_object_id = sha1.hexdigest()
            for child in tree_entry.children:
                if child.tree_id != tree_entry.entry_object_id:
                    child.tree_id = tree_entry.entry_object_id
                    updated_entries.append(child)

        if self.root_entry and not self.root_entry.entry_object_id:
            updated_entries.append(self.root_entry)
            _hash_tree_entry(self.root_entry)

        return updated_entries
