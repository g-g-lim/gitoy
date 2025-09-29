from repository.repository import Repository
from util.console import Console


class Commit:
    """
    gitoy-commit - Record changes to the repository
    """

    def __init__(self, repository: Repository, console: Console):
        self._repository = repository
        self._console = console

    def __call__(self, message: str):
        commit = self._repository.commit(message)
        if commit is None:
            self._console.warning("No changes to commit")
        else:
            self._console.success(
                f"Success commit: {commit.object_id}\n{commit.message}"
            )
