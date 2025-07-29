from pathlib import Path

from util.file import File
from .repo_path import RepositoryPath

class Worktree:
    def __init__(self, repository_path: RepositoryPath):
        self.repo_path = repository_path

    @property
    def root_dir(self) -> Path:
        return self.repo_path.worktree_path

    # TODO: test for absolute path 
    def find_paths(self, path: str) -> list[Path]:
        relative_path = self.repo_path.to_relative_path(path)
        path = self.root_dir / relative_path
        if (path.is_dir()):
            return [p for p in path.rglob("*") if p.is_file()]
        elif (path.is_file()):
            return [path]
        else:
            return []

    def find_files(self, path: str) -> list[File]:
        return [File(p) for p in self.find_paths(path)]
    
    