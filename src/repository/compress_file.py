import mmap
from pathlib import Path
import zstandard

from util.constant import FILE_SIZE_MEDIUM, FILE_SIZE_SMALL


class CompressFile:
    def __init__(self, compression: zstandard.ZstdCompressor):
        self.compression = compression

    def compress(self, path: Path) -> bytes:
        stat = path.stat()
        if stat.st_size <= FILE_SIZE_SMALL:
            return self.compression.compress(path.read_bytes())
        elif stat.st_size <= FILE_SIZE_MEDIUM:
            with open(path, "rb") as f:
                with mmap.mmap(
                    f.fileno(), length=0, access=mmap.ACCESS_READ
                ) as mmap_file:
                    return self.compression.compress(mmap_file)
        else:
            raise NotImplementedError("File is too large")
