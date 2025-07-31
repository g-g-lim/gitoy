from datetime import datetime
from pathlib import Path
from database.entity.blob import Blob
from database.entity.index_entry import IndexEntry
from repository.hash_file import HashFile
from repository.repo_path import RepositoryPath

class Convert:

    def __init__(self, hash_file: HashFile, repo_path: RepositoryPath):
        self.hash_file = hash_file
        self.repo_path = repo_path

    def path_to_index_entry(self, path: Path) -> IndexEntry:
        stat = path.stat()
        object_id = self.hash_file.hash(path)
        file_path = self.repo_path.to_normalized_relative_path(path)
        entry = IndexEntry(
            object_id=object_id,
            file_path=file_path,
            file_mode=oct(stat.st_mode), 
            file_size= stat.st_size,
            ctime=stat.st_ctime,
            mtime=stat.st_mtime, 
            dev=stat.st_dev, 
            inode=stat.st_ino, 
            uid=stat.st_uid, 
            gid=stat.st_gid, 
            stage=0, 
            assume_valid= False, 
            skip_worktree= False, 
            intent_to_add= False
        )
        return entry

    def path_to_blob(self, path: Path) -> Blob:
        hash = self.hash_file.hash(path)
        compressed = self.compress(path)
        blob = Blob(object_id=hash, data=compressed, size=path.stat().st_size, created_at=datetime.now())
        return blob