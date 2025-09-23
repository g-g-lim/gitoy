from typing import Optional
from database.database import Database
from repository.tree import Tree
from database.entity.tree_entry import TreeEntry


class TreeStore:
    def __init__(self, database: Database):
        self.database = database

    def build_commit_tree(self, root_tree_id: str) -> Optional[Tree]:
        # root_tree_db = db.get_tree(commit.tree) - DB에서 루트 TreeEntry 생성
        root_tree = self.database.get_tree_entry(root_tree_id, "tree")
        if root_tree is None:
            return None

        tree = Tree(root_tree)
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
