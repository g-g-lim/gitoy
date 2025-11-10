
from database.entity.index_entry import IndexEntry


class EntryDiff:
    
    def __init__(self, base: list[IndexEntry], target: list[IndexEntry]):
        self.base: dict[str, IndexEntry] = {}
        for entry in base:
            self.base[entry.file_path] = entry
        self.target: dict[str, IndexEntry] = {}
        for entry in target:
            self.target[entry.file_path] = entry
    
    def added(self) -> list[IndexEntry]:
        return [self.base[p] for p in self.base if p not in self.target]
    
    def deleted(self) -> list[IndexEntry]:
        return [self.target[p] for p in self.target if p not in self.base]
    
    def modified(self) -> list[IndexEntry]:
        return [
            self.base[p] for p in self.base
            if p in self.target and self._is_modified(p)
        ]
    
    def _is_modified(self, path: str) -> bool:
        base_entry = self.base[path]
        target_entry = self.target[path]
        return (
            base_entry.file_mode != target_entry.file_mode or
            base_entry.object_id != target_entry.object_id
        )