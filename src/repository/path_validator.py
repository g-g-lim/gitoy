from repository.index_store import IndexStore
from repository.worktree import Worktree
from util.result import Result


class PathValidator:
    def __init__(self, worktree: Worktree, index_store: IndexStore):
        self.worktree = worktree
        self.index_store = index_store

    def validate(self, paths: list[str]) -> Result[None]:
        for path in paths:
            found_index_entries = self.index_store.find_by_paths([path])
            if len(found_index_entries) == 0 and len(self.worktree.match(path)) == 0:
                return Result.Fail(f"Path {path} did not match any files")
        return Result.Ok(None)