from database.database import Database
from database.entity.index_entry import IndexEntry
from repository.repo_path import RepositoryPath
from util.result import Result


class IndexStore:
    def __init__(self, database: Database, repo_path: RepositoryPath):
        self.database = database
        self.repo_path = repo_path

    def create(self, entries: list[IndexEntry]) -> Result:
        if not entries:
            return Result.Ok([])
        self.database.create_index_entries(entries)
        return Result.Ok(entries)

    def update(self, entries: list[IndexEntry]) -> Result:
        if not entries:
            return Result.Ok([])
        # TODO 왜 이렇게 했지..?
        self.database.delete_index_entries(entries)
        self.database.create_index_entries(entries)
        return Result.Ok(entries)

    def delete(self, entries: list[IndexEntry]) -> Result:
        if not entries:
            return Result.Ok([])
        self.database.delete_index_entries(entries)
        return Result.Ok(entries)

    def find_by_paths(self, paths: list[str]) -> list[IndexEntry]:
        relative_paths = self.repo_path.to_normalized_relative_paths(paths)
        return self.database.list_index_entries_by_paths_startwith(relative_paths)

    def find_all(self) -> list[IndexEntry]:
        return self.database.list_index_entries()
