import hashlib
import mmap
from pathlib import Path


class HashFile:
    
    def hash(self, path: Path) -> str:
        stat = path.stat()
        size = stat.st_size
        sha1 = hashlib.sha1()
        
        if size < 32 * 1024:
            sha1.update(path.read_bytes())
            return sha1.hexdigest()
        elif size < 512 * 1024 * 1024:
            with open(path, 'rb') as f:
                with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ) as mmap_file:
                    sha1.update(mmap_file)
                    return sha1.hexdigest()
        else:
            raise ValueError("File is too large")