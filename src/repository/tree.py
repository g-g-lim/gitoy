from typing import Optional
from database.entity.tree_entry import TreeEntry


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
        self.root_tree = root_tree
        self.index = TreeIndex()

    def get_entry(self, path):
        return self.index.get(path)

    def has_entry(self, path):
        return self.get_entry(path) is not None

    def add(self, tree):
        pass

    def remove(self, tree):
        pass

    def update(self, tree):
        pass

    def sync_parent_id(self):
        pass

    def hash(self):
        pass
