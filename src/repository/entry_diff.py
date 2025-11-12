from custom_types import Diff
from database.entity.index_entry import IndexEntry


class EntryDiff:

    def diff(self, base: list[IndexEntry], target: list[IndexEntry]) -> Diff:
        base_dict = {entry.path: entry for entry in base}
        target_dict = {entry.path: entry for entry in target}
        added = [base_dict[p] for p in base_dict if p not in target_dict]
        modified = [
            base_dict[p]
            for p in base_dict
            if p in target_dict and self._is_modified(base_dict[p], target_dict[p])
        ]
        deleted = [target_dict[p] for p in target_dict if p not in base_dict]
        return Diff(added, modified, deleted)

    def _is_modified(self, base_entry: IndexEntry, target_entry: IndexEntry) -> bool:
        return (
            base_entry.mode != target_entry.mode
            or base_entry.object_id != target_entry.object_id
        )
