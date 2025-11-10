from typing import Optional
from database.entity.commit import Commit
from database.entity.index_entry import IndexEntry
from repository.index_store import IndexStore
from repository.tree import Tree
from repository.tree_store import TreeStore
from repository.entry_diff import EntryDiff


class TreeDiffResult:
    def __init__(self, tree: Tree):
        self.tree = tree
        self.added: list[IndexEntry] = []
        self.deleted: list[IndexEntry] = []
        self.modified: list[IndexEntry] = []

    def is_empty(self):
        return (
            len(self.added) == 0 and len(self.deleted) == 0 and len(self.modified) == 0
        )


class TreeDiff:
    def __init__(self, index_store: IndexStore, tree_store: TreeStore):
        self.index_store = index_store
        self.tree_store = tree_store

    def diff(self, commit: Optional[Commit]) -> TreeDiffResult:
        index_entries = self.index_store.find_all()
        commit_tree = self.tree_store.build_commit_tree(
            "" if commit is None else commit.tree_id
        )
        diff_result = TreeDiffResult(commit_tree)
        entry_diff = EntryDiff(index_entries, commit_tree.list_index_entries())
        diff_result.added = entry_diff.added()
        diff_result.deleted = entry_diff.deleted()
        diff_result.modified = entry_diff.modified()
        return diff_result
