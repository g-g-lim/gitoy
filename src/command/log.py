from repository.repository import Repository
from util.console import Console


class Log:
    """
    gitoy log - Show commit logs
    """

    def __init__(self, repository: Repository, console: Console):
        self._repository = repository
        self._console = console

    def __call__(self):
        commit_logs = self._repository.log()
        for commit in commit_logs:
            self._console.warning(f"commit {commit.object_id}")
            self._console.info(
                f"Author: {'-' if commit.author_name == '' else commit.author_name} <{commit.author_email}>"
            )
            self._console.info(f"Date: {commit.author_date}\n")
            self._console.info(f"{commit.message}\n")
