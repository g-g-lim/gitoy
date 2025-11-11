from pathlib import Path
from typing import Optional
from custom_types import Changes, StatusResult
from database.entity.commit import Commit
from repository.blob_store import BlobStore
from repository.commit_store import CommitStore
from repository.compress_file import CompressFile
from repository.index_store import IndexStore
from repository.path_validator import PathValidator
from repository.repo_path import RepositoryPath
from database.database import Database
from repository.tree_store import TreeStore
from database.entity.index_entry import IndexEntry
from repository.entry_diff import DiffResult, EntryDiff
from src.repository.tree import Tree
from util.result import Result
from repository.worktree import Worktree
from repository.hash_file import HashFile
from repository.convert import Convert


class Repository:
    def __init__(
        self,
        database: Database,
        repository_path: RepositoryPath,
        worktree: Worktree,
        compress_file: CompressFile,
        hash_file: HashFile,
        index_store: IndexStore,
        blob_store: BlobStore,
        convert: Convert,
        path_validator: PathValidator,
        tree_store: TreeStore,
        commit_store: CommitStore,
    ):
        self.database = database
        self.path = repository_path
        self.worktree = worktree
        self.compress_file = compress_file
        self.hash_file = hash_file
        self.index_store = index_store
        self.blob_store = blob_store
        self.convert = convert
        self.path_validator = path_validator
        self.tree_store = tree_store
        self.commit_store = commit_store

    @property
    def worktree_path(self):
        return self.path.worktree_path

    def is_initialized(self):
        return self.path.get_repo_dir() is not None and self.database.is_initialized()

    def init(self):
        repo_dir = self.path.create_repo_dir()
        self.database.init()
        self.database.create_main_branch()
        return repo_dir

    def list_branches(self):
        return self.database.list_branches()

    def get_head_branch(self):
        return self.database.get_head_branch()

    # TODO: commit hash 를 참조하는 브랜치 생성하는 경우 처리
    def create_branch(self, name: str, commit_hash: str | None = None):
        head_branch = self.get_head_branch()
        create_ref_name = f"refs/heads/{name}"

        if create_ref_name == head_branch.ref_name:
            return Result.Fail(f"Branch {create_ref_name} already exists")

        if head_branch.target_object_id is None:
            self.database.update_ref(head_branch, {"ref_name": create_ref_name})
            head_branch.ref_name = create_ref_name
            return Result.Ok({"ref": head_branch, "new": False})

        new_branch = self.database.create_branch(name, head_branch.target_object_id)
        return Result.Ok({"ref": new_branch, "new": True})

    def update_head_branch(self, branch_name: str):
        head_branch = self.get_head_branch()
        prev_ref_name = head_branch.ref_name
        create_ref_name = f"refs/heads/{branch_name}"

        if prev_ref_name == create_ref_name:
            return Result.Fail(f"Branch {create_ref_name} already exists")

        self.database.update_ref(head_branch, {"ref_name": create_ref_name})
        head_branch.ref_name = create_ref_name
        return Result.Ok(head_branch)

    # TODO: 브랜치 삭제 시 참조되지 않는 커밋 삭제 처리
    def delete_branch(self, name: str):
        ref_name = f"refs/heads/{name}"
        branch = self.database.get_branch(ref_name)
        if branch is None:
            return Result.Fail(f"Branch {ref_name} not found")
        if branch.head:
            return Result.Fail(f"Branch {ref_name} is the head branch")
        self.database.delete_branch(branch)
        return Result.Ok(None)

    def compress(self, path: Path) -> bytes:
        return self.compress_file.compress(path)

    def hash(self, path: Path) -> str:
        return self.hash_file.hash(path)

    def compare_worktree_to_index(self, paths: list[str]) -> DiffResult:
        index_entries = self.index_store.find_by_paths(paths)
        worktree_paths = self.worktree.find_paths(paths)
        worktree_entries = [self.convert.path_to_index_entry(p) for p in worktree_paths]
        return EntryDiff(worktree_entries, index_entries).diff()

    def compare_index_to_tree(
        self, index_entries: list[IndexEntry], tree: Tree
    ) -> DiffResult:
        return EntryDiff(index_entries, tree.list_index_entries()).diff()

    def add_index(self, paths: list[str]):
        result = self.path_validator.validate(paths)
        if result.failed:
            return result

        diff_result = self.compare_worktree_to_index(paths)

        if diff_result.is_empty():
            return Result.Ok(None)

        self.index_store.create(diff_result.added)
        self.index_store.update(diff_result.modified)
        self.index_store.delete(diff_result.deleted)

        blobs = [
            self.convert.index_entry_to_blob(entry)
            for entry in diff_result.added + diff_result.modified
        ]
        self.blob_store.create(blobs)

        return Result.Ok(None)

    def status(self) -> Result[StatusResult]:
        if not self.is_initialized():
            return Result.Fail("Not a gitoy repository")

        head_branch = self.get_head_branch()
        branch_name = head_branch.branch_name

        worktree_path = self.worktree_path
        index_diff_result = self.compare_worktree_to_index([worktree_path.as_posix()])

        status_result = StatusResult(branch_name)
        status_result.unstaged = Changes(
            index_diff_result.added,
            index_diff_result.modified,
            index_diff_result.deleted,
        )
        status_result.staged = Changes([], [], [])

        if head_branch.target_object_id is None:
            return Result.Ok(status_result)

        head_commit = self.database.get_commit(head_branch.target_object_id)
        if head_commit:
            tree = self.tree_store.build_commit_tree(head_commit.tree_id)
            index_entries = self.database.list_index_entries()
            tree_diff_result = self.compare_index_to_tree(index_entries, tree)
        else:
            tree_diff_result = DiffResult([], [], [])

        status_result.staged.added = tree_diff_result.added
        status_result.staged.modified = tree_diff_result.modified
        status_result.staged.deleted = tree_diff_result.deleted

        return Result.Ok(status_result)

    def commit(self, message: str) -> Optional[Commit]:
        head_branch = self.get_head_branch()
        head_commit = None
        if head_branch.target_object_id is not None:
            head_commit = self.database.get_commit(head_branch.target_object_id)

        commit_tree = self.tree_store.build_commit_tree(
            "" if head_commit is None else head_commit.tree_id
        )
        index_entries = self.index_store.find_all()

        diff_result = self.compare_index_to_tree(index_entries, commit_tree)
        if diff_result.is_empty():
            return None

        for entry in diff_result.added:
            commit_tree.add(entry)
        for entry in diff_result.modified:
            commit_tree.update(entry)
        for entry in diff_result.deleted:
            commit_tree.remove(entry)

        updated_entries = commit_tree.build_object_ids()

        commit_ref_tree = self.tree_store.save_commit_tree(updated_entries)

        assert commit_ref_tree.entry_object_id is not None

        new_commit = self.commit_store.save_commit(
            commit_ref_tree.entry_object_id, message, head_commit
        )

        self.database.update_ref(
            head_branch, {"target_object_id": new_commit.object_id}
        )

        return new_commit

    def log(self) -> list[Commit]:
        head_branch = self.get_head_branch()
        if head_branch.target_object_id is None:
            return []
        commit_logs = self.commit_store.list_commit_logs(head_branch.target_object_id)
        return commit_logs

    def checkout(self, ref_name: str) -> Result[None]:
        ref_name = f"refs/heads/{ref_name}"
        branch = self.database.get_branch(ref_name)
        if branch is None:
            return Result.Fail(f"Branch '{ref_name}' not found")

        head_branch = self.get_head_branch()
        if head_branch.ref_name == branch.ref_name:
            return Result.Ok(None)

        assert branch.target_object_id is not None

        status_result = self.status()
        if status_result.failed:
            return Result.Fail(status_result.error)
            
        changes = status_result.value

        assert changes is not None
        assert changes.staged is not None
        assert changes.unstaged is not None
        staged = changes.staged
        unstaged = changes.unstaged

        if not staged.is_empty() or not unstaged.is_empty():
            return Result.Fail(
                "You have uncommitted changes. Please commit or stash them before checkout."
            )

        checkout_commit = self.database.get_commit(branch.target_object_id)
        assert checkout_commit is not None

        checkout_tree = self.tree_store.build_commit_tree(checkout_commit.tree_id)
        current_index_entries = self.index_store.find_all()
        diff_result = self.compare_index_to_tree( current_index_entries, checkout_tree)
        
        # Apply changes to worktree
        for entry in diff_result.added:
            blob = self.database.get_blob(entry.object_id)
            assert blob is not None
            self.worktree.write(entry, blob.data)
        for entry in diff_result.modified:
            blob = self.database.get_blob(entry.object_id)
            assert blob is not None
            self.worktree.write(entry, blob.data)
        for entry in diff_result.deleted:
            self.worktree.delete(entry)
                
        # Apply changes to index
        self.index_store.delete(diff_result.deleted)
        self.index_store.update(diff_result.modified)
        self.index_store.create(diff_result.added)

        self.database.update_ref(head_branch, {"ref_name": branch.ref_name})

        return Result.Ok(None)
