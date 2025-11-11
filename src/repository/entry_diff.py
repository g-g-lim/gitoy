from typing import NamedTuple
from database.entity.index_entry import IndexEntry


class DiffResult(NamedTuple):
    added: list[IndexEntry]
    modified: list[IndexEntry]
    deleted: list[IndexEntry]

    def is_empty(self) -> bool:
        return (
            len(self.added) == 0 and len(self.modified) == 0 and len(self.deleted) == 0
        )

    def all(self) -> list[IndexEntry]:
        return self.added + self.modified + self.deleted


class EntryDiff:
    def __init__(self, base: list[IndexEntry], target: list[IndexEntry]):
        self.base: dict[str, IndexEntry] = {}
        for entry in base:
            self.base[entry.path] = entry
        self.target: dict[str, IndexEntry] = {}
        for entry in target:
            self.target[entry.path] = entry

    def added(self) -> list[IndexEntry]:
        return [self.base[p] for p in self.base if p not in self.target]

    def deleted(self) -> list[IndexEntry]:
        return [self.target[p] for p in self.target if p not in self.base]

    def modified(self) -> list[IndexEntry]:
        return [
            self.base[p] for p in self.base if p in self.target and self._is_modified(p)
        ]

    def diff(self) -> DiffResult:
        return DiffResult(
            self.added(),
            self.modified(),
            self.deleted(),
        )

    def _is_modified(self, path: str) -> bool:
        base_entry = self.base[path]
        target_entry = self.target[path]
        return (
            base_entry.mode != target_entry.mode
            or base_entry.object_id != target_entry.object_id
        )
