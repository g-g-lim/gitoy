from datetime import datetime
from pathlib import Path
from repository.blob import BlobStore
from repository.index import IndexStore
from util.file import File
from .path import RepositoryPath
from database.database import Database
from database.entity.blob import Blob
from util.result import Result
from .worktree import Worktree
import zstandard
import mmap
from util.hash_algo import HashAlgo


class Repository:
    
    def __init__(
        self, 
        database: Database, 
        repository_path: RepositoryPath, 
        worktree: Worktree, 
        compression: zstandard.ZstdCompressor,
        hash_algo: HashAlgo,
        index_store: IndexStore,
        blob_store: BlobStore
    ):
        self.db = database
        self.path = repository_path
        self.worktree = worktree
        self.compression = compression
        self.hash_algo = hash_algo
        self.index_store = index_store
        self.blob_store = blob_store

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

    def hash(self, file: File) -> str:
        hasher= self.hash_algo.init()
        body= file.read_body()
        if file.is_small:
            hasher.hash(body)
        elif file.is_mid:
            with open(file.path, 'rb') as f:
                with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ) as mmap_file:
                    hasher.hash(mmap_file)
        else:
            raise NotImplementedError("File size is too large")
        return hasher.digest()
    
    def compress(self, file: File) -> bytes:
        if  file.is_mid:
            return self.compression.compress(file.read_body())
        elif file.is_small:
            with open(file.path, 'rb') as f:
                with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ) as mmap_file:
                    return self.compression.compress(mmap_file)
        else:
            raise NotImplementedError("File size is too large")

    def to_blob(self, file: File) -> Blob:
        hash = self.hash(file)
        compressed = self.compress(file)
        blob = Blob(object_id=hash, data=compressed, size=file.size, created_at=datetime.now())
        return blob
    
    def add_index(self, paths: list[str]):
        current_dir = Path.cwd()
        # TODO: 현재 경로가 리포지터리 경로인지 체크하는 로직 command 로 이동
        repo_dir = self.path.get_repo_dir(current_dir)
        if repo_dir is None:
            return Result.Fail("Not in a repository")
        
        matched_files: list[File] = []
        for path in paths:
            files = self.worktree.find_files(path, current_dir)
            if len(files) == 0:
                return Result.Fail(f"Pathspec {path} did not match any files")
            matched_files.extend(files)

        index_entries = [file.to_index_entry(self.hash(file)) for file in matched_files]
        result = self.index_store.save(index_entries)
        created_entry_paths = [entry.file_path for entry in result.value]

        blobs = [self.to_blob(file) for file in matched_files if file.relative_path.as_posix() in created_entry_paths] 
        if len(blobs) == 0:
            return Result.Ok(None)
        
        result = self.blob_store.save(blobs)

        return Result.Ok(None)