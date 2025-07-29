from database.database import Database
from database.entity.index_entry import IndexEntry
from repository.repo_path import RepositoryPath
from util.result import Result


class IndexStore:

    def __init__(self, database: Database, repo_path: RepositoryPath):
        self.database = database
        self.repo_path = repo_path

    def save(self, entries: list[IndexEntry]):
        paths = [entry.file_path for entry in entries]
        existing_entries = self.database.list_index_entries_by_paths(paths)

        # create
        create_entries = []
        for entry in entries:
            for existing in existing_entries:
                if existing.file_path == entry.file_path:
                    break
            else:
                create_entries.append(entry)

        # update
        update_entries = []
        for existing in existing_entries:
            for entry in entries:
                if existing.file_path == entry.file_path and existing != entry:
                    update_entries.append(entry)
                    break

        if len(update_entries) > 0:
            self.database.delete_index_entries(update_entries)
            create_entries.extend(update_entries)
        if len(create_entries) > 0:
            self.database.create_index_entries(create_entries)

        return Result.Ok(create_entries)
    
    def find_by_paths(self, paths: list[str]):
        relative_paths = self.repo_path.to_normalized_relative_paths(paths)
        return self.database.list_index_entries_by_paths_startwith(relative_paths)