import hashlib
import mmap
from pathlib import Path

from util.constant import FILE_SIZE_MEDIUM, FILE_SIZE_SMALL


class HashFile:
    
    def hash(self, path: Path) -> str:
        stat = path.stat()
        size = stat.st_size
        sha1 = hashlib.sha1()
        
        if size <= FILE_SIZE_SMALL:
            sha1.update(path.read_bytes())
            return sha1.hexdigest()
        elif size <= FILE_SIZE_MEDIUM:
            with open(path, 'rb') as f:
                with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ) as mmap_file:
                    sha1.update(mmap_file)
                    return sha1.hexdigest()
        else:
            raise ValueError("File is too large")