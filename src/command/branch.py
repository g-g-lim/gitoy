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
        else:
            self.console.info(f"Branch {result['prev_ref_name']} -> {result['ref'].ref_name} updated")