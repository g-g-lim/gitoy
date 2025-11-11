from pathlib import Path

from src.database.entity.index_entry import IndexEntry
from util.array import unique

from repository.repo_path import RepositoryPath


class Worktree:
    def __init__(self, repository_path: RepositoryPath):
        self.repo_path = repository_path

    @property
    def root_dir(self) -> Path:
        return self.repo_path.worktree_path

    def match(self, path: str) -> list[Path]:
        relative_path: Path = self.repo_path.to_relative_path(path)
        _path: Path = self.root_dir / relative_path
        if _path.is_dir():
            result = []
            for p in _path.rglob("*"):
                if self.repo_path.repo_dir in p.parents:
                    continue
                if p.is_file():
                    result.append(p)
            return result
        elif _path.is_file():
            return [_path]
        else:
            return []

    def find_paths(self, paths: list[str]) -> list[Path]:
        return list(unique([p for path in paths for p in self.match(path)], "as_posix"))

    def write(self, index_entry: IndexEntry, content: bytes) -> Path:
        path = index_entry.absolute_path(self.repo_path.worktree_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            f.write(content)
        path.chmod(int(index_entry.mode, 0))
        return path

    def delete(self, index_entry: IndexEntry) -> None:
        path: Path = index_entry.absolute_path(self.repo_path.worktree_path)
        path.unlink(missing_ok=True)
        # clean up empty parent directories
        parent = path.parent
        while parent != self.repo_path.worktree_path:
            try:
                parent.rmdir()
            except OSError:
                break
            parent = parent.parent
