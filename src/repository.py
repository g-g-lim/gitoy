from database.database import Database
from util.file_handler import FileHandler


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
        prev_ref_name = head_branch.ref_name
        create_ref_name = f"refs/heads/{name}"

        if create_ref_name == head_branch.ref_name:
            return {'ref': head_branch, 'created': False, 'updated': False}

        if head_branch.target_object_id is None:
            self.db.update_ref(head_branch, {'ref_name': create_ref_name})
            head_branch.ref_name = create_ref_name
            return {'ref': head_branch, 'created': False, 'updated': True, 'prev_ref_name': prev_ref_name}

        new_branch = self.db.create_branch(name, head_branch.target_object_id)
        return {'ref': new_branch, 'created': True, 'updated': False}
        
    def update_head_branch(self, branch_name: str):
        head_branch = self.db.get_head_branch()
        prev_ref_name = head_branch.ref_name
        create_ref_name = f"refs/heads/{branch_name}"

        if prev_ref_name == create_ref_name:
            return None

        self.db.update_ref(head_branch, {'ref_name': create_ref_name})
        head_branch.ref_name = create_ref_name
        return {'prev_ref_name': prev_ref_name, 'ref': head_branch}