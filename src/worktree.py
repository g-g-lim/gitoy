from pathlib import Path

from util.repository_file import RepositoryFile

class Worktree:
    def __init__(self, repository_file: RepositoryFile):
        self.root_dir_path = repository_file.repo_dir_path.parent

    def find_paths(self, file_path: str) -> list[Path]:
        result_paths: list[Path] = []
        if file_path in (".", "./"):
            result_paths = list(self.root_dir_path.rglob("*"))
        elif file_path in ("..", "../"):
            parent_dir = self.root_dir_path.parent
            result_paths = list(parent_dir.rglob("*"))
        else:
            if any(char in file_path for char in ["*", "?", "[", "]"]):
                result_paths = list(self.root_dir_path.glob(file_path))
            else:
                candidate = self.root_dir_path / file_path
                if candidate.exists():
                    if candidate.is_file():
                        result_paths = [candidate]
                    elif candidate.is_dir():
                        result_paths = list(candidate.rglob("*"))
                else:
                    result_paths = []
        return result_paths

    
    