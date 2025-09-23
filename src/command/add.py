from repository.repository import Repository
from util.console import Console


class Add:
    """
    gitoy-add - Add file contents to the index
    """

    def __init__(self, repository: Repository, console: Console):
        self._repository = repository
        self._console = console

    def __call__(self, *paths: str):
        result = self._repository.add_index(list(paths))
        if result.failed:
            self._console.error(result.error)
