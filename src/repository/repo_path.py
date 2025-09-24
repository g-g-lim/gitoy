import os
from typing import Optional
from pathlib import Path

from util.constant import GITOY_DB_FILE, GITOY_DIR
from util.path import normalize_path


class RepositoryPath:
    def __init__(self, cwd: Optional[Path] = None, repo_dir_name=GITOY_DIR):
        self.cwd = cwd or Path(os.getcwd())
        self.repo_dir_name = repo_dir_name
        self.repo_dir = self.get_repo_dir()

    @property
    def worktree_path(self):
        repo_dir = self.repo_dir
        if repo_dir is None:
            raise ValueError("Repository directory not found")
        return repo_dir.parent

    def get_repo_dir(self, cwd: Optional[Path] = None) -> Optional[Path]:
        current_path = cwd or self.cwd
        while True:
            repo_dir = current_path / self.repo_dir_name
            if repo_dir.exists() and repo_dir.is_dir():
                return repo_dir
            if current_path.parent == current_path:
                # Reached the root directory
                return None
            current_path = current_path.parent

    def get_repo_db_path(self) -> Optional[Path]:
        repo_dir = self.get_repo_dir()
        if repo_dir is None:
            return None
        return Path(repo_dir, GITOY_DB_FILE)

    def create_repo_dir(self) -> Path:
        if self.repo_dir is not None:
            return self.repo_dir

        self.repo_dir = self.cwd / self.repo_dir_name
        self.repo_dir.mkdir(parents=True, exist_ok=True)
        return self.repo_dir

    def create_repo_db_path(self):
        return Path(self.cwd, self.repo_dir_name, GITOY_DB_FILE)

    def to_relative_path(self, path: str | Path) -> Path:
        if isinstance(path, str):
            path = Path(path)
        return path.resolve().relative_to(self.worktree_path)

    def to_relative_paths(self, paths: list[str | Path]):
        return [self.to_relative_path(path) for path in paths]

    def to_normalized_relative_path(self, path: str | Path) -> Path:
        return normalize_path(self.to_relative_path(path).as_posix())

    def to_normalized_relative_paths(self, paths: list[str | Path]):
        return [self.to_normalized_relative_path(path) for path in paths]
