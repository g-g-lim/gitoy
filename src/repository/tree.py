from database.entity.tree_entry import TreeEntry


class TreeIndex:
    def __init__(self):
        self.cache = {}

    def get(self, path):
        return self.cache.get(path)

    def set(self, path, tree):
        self.cache[path] = tree

    def remove(self, path):
        if path in self.cache:
            del self.cache[path]

    @property
    def size(self):
        return len(self.cache)


class Tree:
    def __init__(self, root_tree: TreeEntry):
        self.root_tree = root_tree
        self.index = TreeIndex()

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
