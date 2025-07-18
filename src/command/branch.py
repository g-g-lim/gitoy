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
        if result.success:
            if result.value['new']:
                self.console.success(f'Branch refs/heads/{name} created')
            else:
                self.console.success(f"Branch {result.value['ref'].ref_name} updated")
        else:
            self.console.error(result.error)

    def update(self, name: str):
        result = self.repository.update_head_branch(name)
        if result.success:
            self.console.success(f"Branch {result.value.ref_name} updated")
        
    def delete(self, name: str):
        result = self.repository.delete_branch(name)
        if result.success:
            self.console.success(f"Branch refs/heads/{name} deleted")
        else:
            self.console.error(result.error)