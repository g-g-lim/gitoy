from typing import Optional
from database.entity.commit import Commit
from database.entity.index_entry import IndexEntry
from repository.index_store import IndexStore
from repository.tree_store import TreeStore


class TreeDiffResult:
    def __init__(self):
        self.added: list[IndexEntry] = []
        self.deleted: list[IndexEntry] = []
        self.modified: list[IndexEntry] = []

    def is_empty(self):
        return (
            len(self.added) == 0 and len(self.deleted) == 0 and len(self.modified) == 0
        )


class TreeDiff:
    def __init__(self, index_store: IndexStore, TreeStore: TreeStore):
        self.index_store = index_store
        self.tree_store = TreeStore

    def diff(self, commit: Optional[Commit]) -> TreeDiffResult:
        index_entries = self.index_store.find_all()
        index_entries_map = {}
        for index_entry in index_entries:
            index_entries_map[index_entry.file_path] = index_entry

        commit_tree = self.tree_store.build_commit_tree(
            "" if commit is None else commit.tree_id
        )
        diff_result = TreeDiffResult()

        for index_entry in index_entries:
            tree_entry = commit_tree.get_entry(index_entry.file_path)
            if tree_entry is None:
                diff_result.added.append(index_entry)
            elif (
                index_entry.file_mode != tree_entry.entry_mode
                or index_entry.object_id != tree_entry.entry_object_id
            ):
                diff_result.modified.append(index_entry)

        for path, tree_entry in commit_tree.index:
            if tree_entry.entry_type == "tree":
                continue
            if path not in index_entries_map:
                index_entry = IndexEntry(
                    file_path=path,
                    file_mode=tree_entry.entry_mode,
                    object_id=tree_entry.entry_object_id,
                )
                diff_result.deleted.append(index_entry)

        return diff_result
