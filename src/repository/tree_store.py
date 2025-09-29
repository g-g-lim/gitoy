from typing import Optional
from database.database import Database
from repository.tree import Tree
from database.entity.tree_entry import TreeEntry


class TreeStore:
    def __init__(self, database: Database):
        self.database = database

    def build_commit_tree(self, root_tree_id: str) -> Optional[Tree]:
        root_tree = self.database.get_root_tree_entry(root_tree_id)
        tree = Tree(root_tree)
        if root_tree is None:
            return tree

        tree.index.set(root_tree.entry_name, root_tree)
        stack = [
            {
                "path": root_tree.entry_name,
                "tree": root_tree,
            }
        ]

        while len(stack) > 0:
            current_item = stack.pop()
            parent_path = current_item["path"]
            parent_tree_entry: TreeEntry = current_item["tree"]
            parent_id = parent_tree_entry.entry_object_id

            children: list[TreeEntry] = self.database.get_child_tree_entries(parent_id)

            for child in children:
                child_path = parent_path + "/" + child.entry_name
                child_tree_entry = tree.index.get(child_path)
                if child_tree_entry is None:
                    child_tree_entry = child
                    tree.index.set(child_path, child_tree_entry)

                parent_tree_entry.append_child(child_tree_entry)

                if child_tree_entry.entry_type == "tree":
                    stack.append(
                        {
                            "path": child_path,
                            "tree": child_tree_entry,
                        }
                    )

        return tree

    def save_commit_tree(self, tree_entries: list[TreeEntry]) -> TreeEntry:
        root_tree = list(filter(lambda x: x.entry_name == ".", tree_entries))[0]
        saved_root_tree = self.database.get_root_tree_entry(root_tree.entry_object_id)
        if saved_root_tree is not None:
            return root_tree

        for entry in tree_entries:
            data = {
                "entry_object_id": entry.entry_object_id,
                "tree_id": entry.tree_id,
                "entry_type": entry.entry_type,
                "entry_name": entry.entry_name,
            }
            saved_entry = self.database.get_tree_entry(data)
            if saved_entry is not None:
                continue
            self.database.create_tree_entry(entry)

        return root_tree
