import hashlib
from pathlib import Path
from repository_path import RepositoryPath
from database.database import Database
from util.result import Result
from worktree import Worktree
import zstandard
import mmap

class Repository:
    
    def __init__(self, 
        database: Database, 
        repository_path: RepositoryPath, 
        worktree: Worktree, 
        compression: zstandard.ZstdCompressor
    ):
        self.db = database
        self.path = repository_path
        self.worktree = worktree
        self.compression = compression

    def is_initialized(self):
        return self.path.get_repo_dir() is not None and self.db.is_initialized()

    def init(self):
        repo_dir = self.path.create_repo_dir()
        self.db.init()
        self.db.create_main_branch()
        return repo_dir

    def list_branches(self):
        return self.db.list_branches()

    def get_head_branch(self):
        return self.db.get_head_branch()

    # TODO: commit hash 를 참조하는 브랜치 생성하는 경우 처리
    def create_branch(self, name: str, commit_hash: str | None = None):
        head_branch = self.get_head_branch()
        create_ref_name = f"refs/heads/{name}"

        if create_ref_name == head_branch.ref_name:
            return Result.Fail(f"Branch {create_ref_name} already exists")

        if head_branch.target_object_id is None:
            self.db.update_ref(head_branch, {'ref_name': create_ref_name})
            head_branch.ref_name = create_ref_name  
            return Result.Ok({'ref': head_branch, 'new': False})

        new_branch = self.db.create_branch(name, head_branch.target_object_id)
        return Result.Ok({'ref': new_branch, 'new': True})
        
    def update_head_branch(self, branch_name: str):
        head_branch = self.db.get_head_branch()
        prev_ref_name = head_branch.ref_name
        create_ref_name = f"refs/heads/{branch_name}"

        if prev_ref_name == create_ref_name:
            return Result.Fail(f"Branch {create_ref_name} already exists")

        self.db.update_ref(head_branch, {'ref_name': create_ref_name})
        head_branch.ref_name = create_ref_name
        return Result.Ok(head_branch)

    # TODO: 브랜치 삭제 시 참조되지 않는 커밋 삭제 처리
    def delete_branch(self, name: str):
        ref_name = f"refs/heads/{name}"
        branch = self.db.get_branch(ref_name)
        if branch is None:
            return Result.Fail(f"Branch {ref_name} not found")
        if branch.head:
            return Result.Fail(f"Branch {ref_name} is the head branch")
        self.db.delete_branch(branch)
        return Result.Ok(None)

    def hash_file(self, path: Path):
        if not path.exists():
            return Result.Fail(f"File {path} not found")

        stat = path.lstat()
        fsize = stat.st_size
        sha1 = hashlib.sha1()

        if fsize <= 32 * 1024:
            body = path.read_bytes()
            sha1.update(body)
            return Result.Ok(sha1.hexdigest())
        elif fsize <= 512 * 1024 * 1024:
            with open(path, 'rb') as f:
                with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ) as mmap_file:
                    sha1.update(mmap_file)
            return Result.Ok(sha1.hexdigest())
        else:
            raise NotImplementedError("File size is too large")

    def compress_file(self, path: Path):
        pass

    def add_to_index(self, add_paths: list[str]):
        current_dir = Path.cwd()
        repo_dir = self.path.get_repo_dir(current_dir)
        if repo_dir is None:
            return Result.Fail("Not in a repository")
        
        matched_paths: list[Path] = []
        for path in add_paths:
            found_paths = self.worktree.find_paths(path, current_dir)
            if len(found_paths) == 0:
                return Result.Fail(f"Pathspec {path} did not match any files")
            matched_paths.extend(found_paths)

        for path in matched_paths:
            hash = self.hash_file(path)
            print(hash)

        return Result.Ok(None)