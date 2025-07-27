import mmap
from pathlib import Path

from database.entity.index_entry import IndexEntry

class File:

    def __init__(self, path: Path, root_dir: Path):
        self.path = path
        self.root_dir = root_dir

    @staticmethod
    def small_size_treshold():
        return 32 * 1024
    
    @staticmethod
    def mid_size_treshold():
        return 512 * 1024 * 1024
    
    @property
    def is_small(self):
        return self.size <= self.small_size_treshold()
    
    @property
    def is_mid(self):
        return self.size <= self.mid_size_treshold()
    
    @property
    def size(self):
        return self.stat().st_size
    
    @property
    def relative_path(self) -> Path:
        return self.path.relative_to(self.root_dir)

    @property
    def exists(self):
        return self.path.exists()
    
    def stat( self):
        return self.path.lstat()
    
    def read_body(self):
        if self.is_small:
            return self.path.read_bytes()
        elif self.is_mid:
            with open(self.path, 'rb') as f:
                return mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ)
        else: 
            raise NotImplementedError("File size is too large")
    
    def to_index_entry(self, object_id: str) -> IndexEntry:
        stat = self.stat()
        entry = IndexEntry(
            object_id=object_id,
            file_path=self.relative_path.as_posix(),
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