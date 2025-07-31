from pathlib import Path

from util.array import unique

from .repo_path import RepositoryPath

class Worktree:
    def __init__(self, repository_path: RepositoryPath):
        self.repo_path = repository_path

    @property
    def root_dir(self) -> Path:
        return self.repo_path.worktree_path

    # TODO: test for absolute path 
    def match(self, path: str) -> list[Path]:
        relative_path = self.repo_path.to_relative_path(path)
        path = self.root_dir / relative_path
        if (path.is_dir()):
            return [p for p in path.rglob("*") if p.is_file()]
        elif (path.is_file()):
            return [path]
        else:
            return []

    def find_paths(self, paths: list[str]) -> list[Path]:
        return list(unique([p for path in paths for p in self.match(path)], 'as_posix'))
    
    