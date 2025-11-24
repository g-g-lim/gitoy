from pathlib import Path
from typing import Optional
from custom_types import StatusResult
from database.entity.commit import Commit
from repository.blob_store import BlobStore
from repository.commit_store import CommitStore
from repository.compress_file import CompressFile
from repository.index_store import IndexStore
from repository.path_validator import PathValidator
from repository.repo_path import RepositoryPath
from database.database import Database
from repository.tree_store import TreeStore
from repository.entry_diff import EntryDiff
from database.entity.ref import Ref
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
        entry_diff: EntryDiff,
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
        self.entry_diff = entry_diff

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

        # 헤드 브랜치가 아직 커밋을 가리키지 않는 경우 헤드 브랜치를 새 브랜치로 변경
        if head_branch.target_object_id is None:
            self.database.update_ref(head_branch, {"ref_name": create_ref_name})
            head_branch.ref_name = create_ref_name
            return Result.Ok({"ref": head_branch, "new": False})

        new_branch = self.database.create_branch(name, head_branch.target_object_id)
        return Result.Ok({"ref": new_branch, "new": True})

    def update_head_branch_name(self, branch_name: str):
        head_branch = self.get_head_branch()
        prev_ref_name = head_branch.ref_name
        create_ref_name = f"refs/heads/{branch_name}"

        if prev_ref_name == create_ref_name:
            return Result.Fail(f"Branch {create_ref_name} already exists")

        self.database.update_ref(head_branch, {"ref_name": create_ref_name})
        head_branch.ref_name = create_ref_name
        return Result.Ok(head_branch)

    def update_head_branch(self, from_ref: Ref, to_ref: Ref):
        if from_ref.ref_name == to_ref.ref_name:
            return Result.Fail(f"Branch {to_ref.ref_name} is already the head branch")

        self.database.update_ref(from_ref, {"head": False})
        self.database.update_ref(to_ref, {"head": True})

        return Result.Ok(to_ref)

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

    def add_index(self, paths: list[str]):
        result = self.path_validator.validate(paths)
        if result.failed:
            return result

        diff_result = self.get_unstaged_changes(paths)
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
    
    def get_unstaged_changes(self, paths): # TODO parameter type
        index_entries = self.index_store.find_by_paths(paths)
        worktree_paths = self.worktree.find_paths(paths)
        worktree_entries = [self.convert.path_to_index_entry(p) for p in worktree_paths]
        return self.entry_diff.diff(worktree_entries, index_entries)
        
    def get_staged_changes(self, ref: Ref):
        tree_id = ""
        if ref.target_object_id is not None:
            head_commit = self.database.get_commit(ref.target_object_id)
            assert head_commit is not None
            tree_id = head_commit.tree_id

        tree = self.tree_store.build_commit_tree(tree_id)
        index_entries = self.database.list_index_entries()
        return self.entry_diff.diff(index_entries, tree.list_index_entries())

    def status(self) -> Result[StatusResult]:
        if not self.is_initialized():
            return Result.Fail("Not a gitoy repository")
        head_branch = self.get_head_branch()
        branch_name = head_branch.branch_name
        
        result = StatusResult(branch_name)
        result.unstaged = self.get_unstaged_changes([self.worktree_path.as_posix()])
        result.staged = self.get_staged_changes(head_branch)
        return Result.Ok(result)

    def commit(self, message: str) -> Optional[Commit]:
        head_branch = self.get_head_branch()
        head_commit = None
        if head_branch.target_object_id is not None:
            head_commit = self.database.get_commit(head_branch.target_object_id)
            
        tree_id = ""
        if head_branch.target_object_id is not None:
            head_commit = self.database.get_commit(head_branch.target_object_id)
            assert head_commit is not None
            tree_id = head_commit.tree_id
        
        commit_tree = self.tree_store.build_commit_tree(tree_id)
        index_entries = self.database.list_index_entries()
        diff = self.entry_diff.diff(index_entries, commit_tree.list_index_entries())
    
        staged = self.get_staged_changes(head_branch)
        if staged.is_empty():
            return None

        updated_entries = commit_tree.apply_diff(diff)
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
        checkout_branch = self.database.get_branch(ref_name)
        if checkout_branch is None:
            return Result.Fail(f"Branch '{ref_name}' not found")

        head_branch = self.get_head_branch()
        if head_branch.ref_name == checkout_branch.ref_name:
            return Result.Ok(None)

        unstaged= self.get_unstaged_changes([self.worktree_path.as_posix()])
        staged = self.get_staged_changes(head_branch)

        if not staged.is_empty() or not unstaged.is_empty():
            return Result.Fail(
                "You have uncommitted changes. Please commit or stash them before checkout."
            )
        
        assert checkout_branch.target_object_id is not None
        checkout_commit = self.database.get_commit(checkout_branch.target_object_id)
        assert checkout_commit is not None
        checkout_tree = self.tree_store.build_commit_tree(checkout_commit.tree_id)
        current_index_entries = self.index_store.find_all()
        diff = self.entry_diff.diff(
            checkout_tree.list_index_entries(), current_index_entries
        )

        # Apply changes to worktree
        for entry in diff.added:
            blob = self.database.get_blob(entry.object_id)
            assert blob is not None
            self.worktree.write(entry, self.compress_file.decompress(blob.data))
            entry.size = blob.size
        for entry in diff.modified:
            blob = self.database.get_blob(entry.object_id)
            assert blob is not None
            self.worktree.write(entry, self.compress_file.decompress(blob.data))
            entry.size = blob.size
        for entry in diff.deleted:
            self.worktree.delete(entry)

        # Apply changes to index
        self.index_store.delete(diff.deleted)
        self.index_store.update(diff.modified)
        self.index_store.create(diff.added)

        self.update_head_branch(head_branch, checkout_branch)

        return Result.Ok(None)