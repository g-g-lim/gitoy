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
        if status_result.failed and status_result.error:
            self._console.error(status_result.error)
            return

        assert status_result.value is not None

        status_result = status_result.value
        branch_name = status_result.branch_name
        staged = status_result.staged
        unstaged = status_result.unstaged

        assert staged is not None
        assert unstaged is not None

        self._console.info(f"On branch {branch_name}")
        self._console.info("")

        worktree_path = self._repository.worktree_path

        if staged.added or staged.modified or staged.deleted:
            self._console.info("staged")
            self._console.info("")
            for changed_entry in staged.added:
                self._console.log(
                    f"new file: {changed_entry.relative_path(worktree_path)}", "green"
                )
            for changed_entry in staged.modified:
                self._console.log(
                    f"modified: {changed_entry.relative_path(worktree_path)}", "green"
                )
            for changed_entry in staged.deleted:
                self._console.log(
                    f"deleted: {changed_entry.relative_path(worktree_path)}", "green"
                )
            self._console.info("")

        if unstaged.modified or unstaged.deleted:
            self._console.info("unstaged")
            self._console.info("")
            for changed_entry in unstaged.modified:
                self._console.log(
                    f"modified: {changed_entry.relative_path(worktree_path)}", "yellow"
                )
            for changed_entry in unstaged.deleted:
                self._console.log(
                    f"deleted: {changed_entry.relative_path(worktree_path)}", "red"
                )
            self._console.info("")

        if unstaged.added:
            self._console.info("untracked")
            self._console.info("")
            for changed_entry in unstaged.added:
                self._console.log(
                    f"new file: {changed_entry.relative_path(worktree_path)}", "red"
                )
