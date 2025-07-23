from datetime import datetime
from typing import Optional
from database.sqlite import SQLite
from database.entity.blob import Blob
from database.entity.commit import Commit
from database.entity.ref import Ref
from database.entity.reflog import Reflog
from database.entity.tag import Tag
from database.entity.tree import Tree
from database.entity.tree_entry import TreeEntry
from database.entity.index_entry import IndexEntry


class Database: 

    def __init__(self, sqlite: SQLite):
        self.sqlite = sqlite
        self.entity_list = [
            Blob,
            Commit,
            Ref,
            Reflog,
            Tag,
            Tree,
            TreeEntry,
            IndexEntry,
        ]

    def is_initialized(self) -> bool:
        return self.sqlite.path is not None and self.sqlite.path.exists() and len(self.sqlite.list_tables()) == len(self.entity_list)

    def init(self) -> None:
        for entity in self.entity_list:
            self.sqlite.create_table(entity.table_name(), entity.columns())

    def create_main_branch(self) -> Ref:
        ref = Ref(
            ref_name="refs/heads/main",
            ref_type="branch",
            head=True,
            is_symbolic=False,
            updated_at=datetime.now(),
            target_object_id=None,
            symbolic_target=None,
            namespace=None,
        )
        self.sqlite.insert(ref)
        return ref

    def list_branches(self) -> list[Ref]:
        refs = self.sqlite.select(f"SELECT * FROM {Ref.table_name()} WHERE ref_type = 'branch'")
        return [Ref(**ref) for ref in refs]

    def create_branch(self, branch_name: str, target_object_id: Optional[str] = None) -> Ref:
        ref = Ref(
            ref_name=f"refs/heads/{branch_name}",
            ref_type="branch",
            head=False,
            is_symbolic=False,
            updated_at=datetime.now(),
            target_object_id=target_object_id,
            symbolic_target=None,
            namespace=None,
        )
        self.sqlite.insert(ref)
        return ref
    
    def get_head_branch(self) -> Ref:
        refs = self.sqlite.select(f"SELECT * FROM {Ref.table_name()} WHERE head = 1 AND ref_type = 'branch'")
        return Ref(**refs[0])
    
    def update_ref(self, ref: Ref, update_values: dict) -> Ref:
        self.sqlite.update(ref, update_values)
        return ref

    def get_branch(self, name: str) -> Optional[Ref]:
        refs = self.sqlite.select(f"SELECT * FROM {Ref.table_name()} WHERE ref_name = '{name}' AND ref_type = 'branch'")
        return Ref(**refs[0]) if refs else None

    def delete_branch(self, branch: Ref) -> None:
        self.sqlite.delete(branch)

    def create_blob(self, blob: Blob) -> None:
        return self.sqlite.insert(Blob)

    def create_blobs(self, blobs: list[Blob]) -> None:
        self.sqlite.insert_many(blobs)