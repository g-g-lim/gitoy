from util.file_handler import FileHandler
from database.database import Database
from util.result import Result


class Repository:
    def __init__(self, database: Database, file_handler: FileHandler):
        self.db = database
        self.file_handler = file_handler

    def is_initialized(self):
        return self.file_handler.repo_dir is not None and self.db.is_initialized()

    def init(self):
        repo_dir = self.file_handler.create_repo_dir()
        self.db.init()
        self.db.create_main_branch()
        return repo_dir

    def list_branches(self):
        return self.db.list_branches()

    def get_head_branch(self):
        return self.db.get_head_branch()

    def create_branch(self, name: str):
        head_branch = self.get_head_branch()
        create_ref_name = f"refs/heads/{name}"

        if create_ref_name == head_branch.ref_name:
            return Result(False, None, "Branch already exists")

        if head_branch.target_object_id is None:
            self.db.update_ref(head_branch, {'ref_name': create_ref_name})
            head_branch.ref_name = create_ref_name  
            return Result(True, {'ref': head_branch, 'new': False}, None)

        new_branch = self.db.create_branch(name, head_branch.target_object_id)
        return Result(True, {'ref': new_branch, 'new': True}, None)
        
    def update_head_branch(self, branch_name: str):
        head_branch = self.db.get_head_branch()
        prev_ref_name = head_branch.ref_name
        create_ref_name = f"refs/heads/{branch_name}"

        if prev_ref_name == create_ref_name:
            return Result(False, None, "Branch already exists")

        self.db.update_ref(head_branch, {'ref_name': create_ref_name})
        head_branch.ref_name = create_ref_name
        return Result(True, head_branch, None)

    def delete_branch(self, name: str):
        ref_name = f"refs/heads/{name}"
        branch = self.db.get_branch(ref_name)
        if branch is None:
            return Result(False, None, f"Branch {ref_name} not found")
        if branch.head:
            return Result(False, None, f"Branch {ref_name} is the head branch")
        self.db.delete_branch(branch)
        return Result(True, None, None)