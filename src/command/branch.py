from repository.repository import Repository
from util.console import Console


class Branch:
    """ 
    gitoy branch - List, create, or delete branches
    """

    def __init__(self, repository: Repository, console: Console):
        self._repository = repository
        self._console = console

    def __call__(self):
        branches = self._repository.list_branches()
        sorted_branches = sorted(branches, key=lambda x: (x.head, x.branch_name))
        for branch in sorted_branches:
            if branch.head:
                self._console.success(f"* {branch.branch_name}")
            else:
                self._console.info(branch.branch_name)

    def create(self, name: str, commit_hash: str):
        result = self._repository.create_branch(name, commit_hash)
        if result.success:
            if result.value['new']:
                self._console.success(f'Branch refs/heads/{name} created')
            else:
                self._console.success(f"Branch {result.value['ref'].ref_name} updated")
        else:
            self._console.error(result.error)

    def update(self, name: str):
        result = self._repository.update_head_branch(name)
        if result.success:
            self._console.success(f"Branch {result.value.ref_name} updated")
        
    def delete(self, name: str):
        result = self._repository.delete_branch(name)
        if result.success:
            self._console.success(f"Branch refs/heads/{name} deleted")
        else:
            self._console.error(result.error)