from database.entity.index_entry import IndexEntry
from repository.convert import Convert
from repository.index_store import IndexStore
from repository.worktree import Worktree


class IndexDiff:

    def __init__(self, index_store: IndexStore, worktree: Worktree, convert: Convert):
        self.index_store = index_store
        self.worktree = worktree
        self.convert = convert

    def diff(self, paths: list[str]):
        index_entries = self.index_store.find_by_paths(paths)
        worktree_paths = self.worktree.find_paths(paths)
        worktree_entries = [self.convert.path_to_index_entry(p) for p in worktree_paths]

        print('index_entries', index_entries)
        print('worktree_entries', worktree_entries)

        diff_result: dict[str, list[IndexEntry]] = {
            'added': [],
            'deleted': [],
            'modified': [],
        }

        for worktree_entry in worktree_entries:
            if not any(index_entry.file_path == worktree_entry.file_path for index_entry in index_entries):
                diff_result['added'].append(worktree_entry)

        for index_entry in index_entries:
            if not any(index_entry.file_path == worktree_entry.file_path for worktree_entry in worktree_entries):
                diff_result['deleted'].append(index_entry)

        for index_entry in index_entries:
            for worktree_entry in worktree_entries:
                if index_entry.file_path == worktree_entry.file_path:
                    if index_entry != worktree_entry:
                        diff_result['modified'].append(worktree_entry)

        return diff_result