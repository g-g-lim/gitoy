from pathlib import Path
from typing import Optional

from util.file import File
from .repo_path import RepositoryPath

class Worktree:
    def __init__(self, repository_path: RepositoryPath):
        self.repo_path = repository_path

    @property
    def root_dir(self) -> Path:
        return self.repo_path.worktree_path

    # TODO: test for absolute path 
    def find_files(self, path: str, start_dir: Optional[Path] = None) -> list[File]:
        root_dir = self.root_dir
        start_dir = start_dir or Path.cwd()
        files = []
        
        if path in (".", "./"):
            files = [File(p, root_dir) for p in start_dir.rglob("*") if p.is_file()]
        elif path in ("..", "../"):
            parent_dir = start_dir.parent
            files = [File(p, root_dir) for p in parent_dir.rglob("*") if p.is_file()]
        else:
            # TODO: write test code for glob pattern
            if any(char in path for char in ["*", "?", "[", "]"]):
                files = [File(p, root_dir) for p in start_dir.rglob(path) if p.is_file()]
            else:
                candidate = start_dir / path
                if candidate.exists():
                    if candidate.is_file():
                        files = [File(candidate, root_dir)]
                    elif candidate.is_dir():
                        files = [File(p, root_dir) for p in candidate.rglob("*") if p.is_file()]
        return files
    
    