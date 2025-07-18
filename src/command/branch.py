from repository import Repository
from util.console import Console


class Branch:
    """ 
    gitoy branch - List, create, or delete branches
    """

    def __init__(self, repository: Repository, console: Console):
        self.repository = repository
        self.console = console

    def __call__(self):
        branches = self.repository.list_branches()
        sorted_branches = sorted(branches, key=lambda x: (x.head, x.branch_name))
        for branch in sorted_branches:
            if branch.head:
                self.console.success(f"* {branch.branch_name}")
            else:
                self.console.info(branch.branch_name)

    def create(self, name: str):
        result = self.repository.create_branch(name)
        if result['created']:
            self.console.success(f"Branch {name} created")
        elif result['updated']:
            self.console.info(f"Branch {result['prev_ref_name']} -> {result['ref'].ref_name} updated")
        else:
            self.console.info(f"Branch refs/heads/{name} already exists")
    
    def update(self, name: str):
        result = self.repository.update_head_branch(name)
        if result is not None:
            self.console.success(f"Branch {result['prev_ref_name']} -> {result['ref'].ref_name} updated")
        
    def delete(self, name: str):
        result = self.repository.delete_branch(name)
        if 'deleted' in result and result['deleted']:
            self.console.success(f"Branch refs/heads/{name} deleted")
        elif 'not_found' in result and result['not_found']:
            self.console.error(f"Branch refs/heads/{name} not found")
        else:
            self.console.error(f"Branch refs/heads/{name} is the head branch")