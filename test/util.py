from database.entity.tree_entry import TreeEntry


def check_parent_child_id(tree_entry: TreeEntry):
    for child in tree_entry.children:
        if child.entry_type == "tree" and child.entry_object_id is None:
            check_parent_child_id(child)
    for child in tree_entry.children:
        assert child.tree_id == tree_entry.entry_object_id
