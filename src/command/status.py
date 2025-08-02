from repository.repository import Repository
from util.console import Console


class Status:
    """
    gitoy status - Show the working tree status
    """

    def __init__(self, repository: Repository, console: Console):
        self._repository = repository
        self._console = console

    def __call__(self): 
        status_result = self._repository.status()
        if status_result.failed:
            self._console.error(status_result.error)
            return

        status_data = status_result.value
        branch_name = status_data['branch_name']
        unstaged = status_data['unstaged']
        untracked = status_data['untracked']

        self._console.info(f"On branch {branch_name}")
        self._console.info("")

        worktree_path = self._repository.worktree_path

        if unstaged['modified'] or unstaged['deleted']:
            self._console.info("unstaged")
            self._console.info("")
            for file_path in unstaged['modified']:
                self._console.log(f"modified: {file_path.relative_to(worktree_path)}", "yellow")
            for file_path in unstaged['deleted']:
                self._console.log(f"deleted: {file_path.relative_to(worktree_path)}", "red")
            self._console.info("")

        if untracked:
            self._console.info("untracked")
            self._console.info("")
            for file_path in untracked:
                self._console.log(f"new file: {file_path.relative_to(worktree_path)}", "red")