
from repository.index_store import IndexStore
from repository.worktree import Worktree


class IndexDiff:

    def __init__(self, index_store: IndexStore, worktree: Worktree):
        self.index_store = index_store
        self.worktree = worktree

    def diff(paths: list[str]):
        pass