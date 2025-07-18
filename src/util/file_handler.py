import os
from typing import Optional
from pathlib import Path

from util.constant import GITOY_DB_FILE, GITOY_DIR

class FileHandler:

    def __init__(self):
        self.cwd = Path(os.getcwd())
        self.repo_dir = self.get_repo_dir()
        self.repo_db_file = self.get_repo_db_file()
    
    def get_repo_db_file(self) -> Optional[Path]:
        if self.repo_dir is None:
            return None
        return Path(self.repo_dir, GITOY_DB_FILE)
    
    def create_repo_db_file(self):
        if self.repo_dir is None:
            self.repo_dir = self.create_repo_dir()
        path = Path(self.repo_dir, GITOY_DB_FILE)
        return path

    def get_repo_dir(self) -> Optional[Path]:
        current_path = self.cwd
        while True:
            repo_dir = current_path / GITOY_DIR
            if repo_dir.exists() and repo_dir.is_dir():
                return repo_dir
            if current_path.parent == current_path:
                # Reached the root directory
                return None
            current_path = current_path.parent
    
    def create_repo_dir(self):
        path = Path(self.cwd, GITOY_DIR)
        path.mkdir(parents=True, exist_ok=True)
        return path