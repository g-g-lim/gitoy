import mmap
from pathlib import Path

class File:

    def __init__(self, path: Path):
        self.path = path

    @staticmethod
    def small_size_treshold():
        return 32 * 1024
    
    @staticmethod
    def mid_size_treshold():
        return 512 * 1024 * 1024
    
    @property
    def size(self):
        return self.path.stat().st_size
    
    @property
    def is_small(self):
        return self.size <= self.small_size_treshold()
    
    @property
    def is_mid(self):
        return self.size <= self.mid_size_treshold()
    
    def read_body(self):
        if self.is_small:
            return self.path.read_bytes()
        elif self.is_mid:
            with open(self.path, 'rb') as f:
                return mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ)
        else: 
            raise NotImplementedError("File size is too large")
        