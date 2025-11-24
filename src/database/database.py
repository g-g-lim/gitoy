from datetime import datetime
from typing import Any, Iterable, Optional
from database.entity.commit_parent import CommitParent
from database.sqlite import SQLite
from database.entity.blob import Blob
from database.entity.commit import Commit
from database.entity.ref import Ref
from database.entity.reflog import Reflog
from database.entity.tag import Tag
from database.entity.tree_entry import TreeEntry
from database.entity.index_entry import IndexEntry


class Database:
    def __init__(self, sqlite: SQLite):
        self.sqlite = sqlite
        self.entity_list = [
            Blob,
            Commit,
            CommitParent,
            Ref,
            Reflog,
            Tag,
            TreeEntry,
            IndexEntry,
        ]

    @staticmethod
    def build_where_clause(query: str, data: dict) -> tuple[str, Iterable[Any]]:
        where = []
        params = []
        for key, value in data.items():
            if value is not None:
                where.append(f"{key} = ?")
                params.append(value)
            else:
                where.append(f"{key} IS NULL")
        return query + " WHERE " + " AND ".join(where), params

    def is_initialized(self) -> bool:
        return (
            self.sqlite.path is not None
            and self.sqlite.path.exists()
            and len(self.sqlite.list_tables()) == len(self.entity_list)
        )

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
        refs = self.sqlite.select(
            f"SELECT * FROM {Ref.table_name()} WHERE ref_type = 'branch'"
        )
        return [Ref(**ref) for ref in refs]

    def create_branch(
        self, branch_name: str, target_object_id: Optional[str] = None
    ) -> Ref:
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
        refs = self.sqlite.select(
            f"SELECT * FROM {Ref.table_name()} WHERE head = 1 AND ref_type = 'branch'"
        )
        return Ref(**refs[0])

    def update_ref(self, ref: Ref, update_values: dict) -> Ref:
        self.sqlite.update(ref, update_values)
        return ref

    def get_branch(self, name: str) -> Optional[Ref]:
        refs = self.sqlite.select(
            f"SELECT * FROM {Ref.table_name()} WHERE ref_name = '{name}' AND ref_type = 'branch'"
        )
        return Ref(**refs[0]) if refs else None

    def delete_branch(self, branch: Ref) -> None:
        self.sqlite.delete(branch)

    def create_blob(self, blob: Blob) -> None:
        return self.sqlite.insert(Blob)

    def create_blobs(self, blobs: list[Blob]) -> None:
        return self.sqlite.insert_many(blobs)

    def get_blob(self, object_id: str) -> Optional[Blob]:
        blobs = self.sqlite.select(
            f"SELECT * FROM {Blob.table_name()} WHERE object_id = '{object_id}'"
        )
        return Blob(**blobs[0]) if blobs else None

    def list_blobs_by_ids(self, object_ids: list[str]) -> list[Blob]:
        id_params = ",".join([f"'{obj_id}'" for obj_id in object_ids])
        blobs = self.sqlite.select(
            f"SELECT * FROM {Blob.table_name()} WHERE object_id IN ({id_params})"
        )
        return [Blob(**blob) for blob in blobs]

    def list_index_entries_by_paths(self, paths: list[str]) -> list[IndexEntry]:
        path_params = ",".join([f"'{path}'" for path in paths])
        index_entries = self.sqlite.select(
            f"SELECT * FROM {IndexEntry.table_name()} WHERE path IN ({path_params})"
        )
        return [IndexEntry(**index_entry) for index_entry in index_entries]

    def list_index_entries_by_paths_startwith(
        self, paths: list[str]
    ) -> list[IndexEntry]:
        like_conditions = " OR ".join([f"path LIKE '{path}%'" for path in paths])
        index_entries = self.sqlite.select(
            f"SELECT * FROM {IndexEntry.table_name()} WHERE {like_conditions}"
        )
        return [IndexEntry(**index_entry) for index_entry in index_entries]

    def list_index_entries(self) -> list[IndexEntry]:
        index_entries = self.sqlite.select(f"SELECT * FROM {IndexEntry.table_name()}")
        return [IndexEntry(**index_entry) for index_entry in index_entries]

    def create_index_entries(self, index_entries: list[IndexEntry]) -> None:
        return self.sqlite.insert_many(index_entries)

    def delete_index_entries(self, entries: list[IndexEntry]) -> None:
        return self.sqlite.delete_many(entries)

    def get_tree_entry(self, data: dict) -> TreeEntry | None:
        query, params = self.build_where_clause(
            f"SELECT * FROM {TreeEntry.table_name()}", data
        )
        tree_entries = self.sqlite.select(query, params)
        return TreeEntry(**tree_entries[0]) if tree_entries else None

    def get_root_tree_entry(self, object_id: str) -> TreeEntry | None:
        tree_entries = self.sqlite.select(
            f"SELECT * FROM {TreeEntry.table_name()} WHERE entry_object_id = '{object_id}' and entry_type = 'tree' and entry_name = '.'",
        )
        return TreeEntry(**tree_entries[0]) if tree_entries else None

    def get_child_tree_entries(self, tree_id: str) -> list[TreeEntry]:
        tree_entries = self.sqlite.select(
            f"SELECT * FROM {TreeEntry.table_name()} WHERE tree_id = '{tree_id}'"
        )
        return [TreeEntry(**tree_entry) for tree_entry in tree_entries]

    def create_tree_entry(self, tree_entry: TreeEntry) -> None:
        return self.sqlite.insert(tree_entry)

    def create_tree_entries(self, tree_entries: list[TreeEntry]) -> None:
        return self.sqlite.insert_many(tree_entries)

    def get_commit(self, object_id: str) -> Optional[Commit]:
        commits = self.sqlite.select(
            f"SELECT * FROM {Commit.table_name()} WHERE object_id = '{object_id}'"
        )
        return Commit(**commits[0]) if commits else None
    
    def list_commits(self, object_ids: list[str]) -> list[Commit]:
        id_params = ",".join([f"'{path}'" for path in object_ids])
        commits = self.sqlite.select(
            f"SELECT * FROM {Commit.table_name()} WHERE object_id IN ({id_params})"
        )
        return [Commit(**commit) for commit in commits]

    def get_commit_children(self, parent_object_id: str) -> list[CommitParent]:
        commit_children = self.sqlite.select(
            f"SELECT * FROM {CommitParent.table_name()} WHERE parent_id = '{parent_object_id}'"
        )
        return [CommitParent(**child) for child in commit_children]

    def get_commit_parents(self, child_object_id: str):
        commit_parents = self.sqlite.select(
            f"SELECT * FROM {CommitParent.table_name()} WHERE commit_id = '{child_object_id}'"
        )
        return [CommitParent(**parent) for parent in commit_parents]

    def create_commit(self, commit: Commit):
        return self.sqlite.insert(commit)

    def create_commit_parent(self, commit_parent: CommitParent):
        return self.sqlite.insert(commit_parent)
