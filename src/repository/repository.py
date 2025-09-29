from pathlib import Path
from custom_types import StatusData
from repository.blob_store import BlobStore
from repository.commit_store import CommitStore
from repository.compress_file import CompressFile
from repository.index_diff import IndexDiff
from repository.index_store import IndexStore
from repository.path_validator import PathValidator
from repository.repo_path import RepositoryPath
from database.database import Database
from repository.tree_diff import TreeDiff
from repository.tree_store import TreeStore
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
        index_diff: IndexDiff,
        path_validator: PathValidator,
        tree_store: TreeStore,
        tree_diff: TreeDiff,
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
        self.index_diff = index_diff
        self.path_validator = path_validator
        self.tree_store = tree_store
        self.tree_diff = tree_diff
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

    def add_index(self, paths: list[str]):
        result = self.path_validator.validate(paths)
        if result.failed:
            return result

        diff_result = self.index_diff.diff(paths)

        if diff_result.is_empty():
            return Result.Ok(None)

        self.index_store.create(diff_result.added)
        self.index_store.update(diff_result.modified)
        self.index_store.delete(diff_result.deleted)

        blobs = [
            self.convert.index_entry_to_blob(entry)
            for entry in diff_result.should_create_blob_entries()
        ]
        self.blob_store.create(blobs)

        return Result.Ok(None)

    def status(self) -> Result[StatusData]:
        if not self.is_initialized():
            return Result.Fail("Not a gitoy repository")

        head_branch = self.get_head_branch()
        branch_name = head_branch.branch_name

        worktree_path = self.worktree_path
        index_diff_result = self.index_diff.diff([worktree_path.as_posix()])
        untracked = [
            entry.absolute_path(worktree_path) for entry in index_diff_result.added
        ]
        unstaged = {
            "modified": [
                entry.absolute_path(worktree_path)
                for entry in index_diff_result.modified
            ],
            "deleted": [
                entry.absolute_path(worktree_path)
                for entry in index_diff_result.deleted
            ],
        }

        head_commit = self.database.get_commit(head_branch.target_object_id)
        tree_diff_result = self.tree_diff.diff(head_commit)
        staged = {
            "added": [
                entry.absolute_path(worktree_path) for entry in tree_diff_result.added
            ],
            "modified": [
                entry.absolute_path(worktree_path)
                for entry in tree_diff_result.modified
            ],
            "deleted": [
                entry.absolute_path(worktree_path) for entry in tree_diff_result.deleted
            ],
        }

        return Result.Ok(
            {
                "branch_name": branch_name,
                "staged": staged,
                "unstaged": unstaged,
                "untracked": untracked,
            }
        )

    def commit(self, message: str):
        head_branch = self.get_head_branch()
        head_commit = self.database.get_commit(head_branch.target_object_id)

        tree_diff_result = self.tree_diff.diff(head_commit)
        commit_tree = tree_diff_result.tree
        for entry in tree_diff_result.added:
            commit_tree.add(entry)
        for entry in tree_diff_result.modified:
            commit_tree.update(entry)
        for entry in tree_diff_result.deleted:
            commit_tree.remove(entry)

        updated_entries = commit_tree.build_object_ids()

        commit_ref_tree = self.tree_store.save_commit_tree(updated_entries)
        new_commit = self.commit_store.save_commit(
            commit_ref_tree.entry_object_id, message, head_commit
        )

        self.database.update_ref(
            head_branch, {"target_object_id": new_commit.object_id}
        )

        return new_commit
