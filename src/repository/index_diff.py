from repository.convert import Convert
from repository.index_store import IndexStore
from repository.worktree import Worktree


class IndexDiffResult:
    def __init__(self):
        self.added = []
        self.deleted = []
        self.modified = []

    def is_empty(self):
        return len(self.added) == 0 and len(self.deleted) == 0 and len(self.modified) == 0

    def should_create_blob_entries(self):
        return self.added + self.modified


class IndexDiff:

    def __init__(self, index_store: IndexStore, worktree: Worktree, convert: Convert):
        self.index_store = index_store
        self.worktree = worktree
        self.convert = convert

    def diff(self, paths: list[str]) -> IndexDiffResult:
        index_entries = self.index_store.find_by_paths(paths)
        worktree_paths = self.worktree.find_paths(paths)
        worktree_entries = [self.convert.path_to_index_entry(p) for p in worktree_paths]

        diff_result = IndexDiffResult()

        for worktree_entry in worktree_entries:
            if not any(index_entry.file_path == worktree_entry.file_path for index_entry in index_entries):
                diff_result.added.append(worktree_entry)

        for index_entry in index_entries:
            if not any(index_entry.file_path == worktree_entry.file_path for worktree_entry in worktree_entries):
                diff_result.deleted.append(index_entry)

        for index_entry in index_entries:
            for worktree_entry in worktree_entries:
                if index_entry.file_path == worktree_entry.file_path:
                    if index_entry != worktree_entry:
                        diff_result.modified.append(worktree_entry)

        return diff_result