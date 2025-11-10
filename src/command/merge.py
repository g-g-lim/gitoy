from repository.repository import Repository
from util.console import Console


class Merge:
    """
    gitoy-merge - Join two or more development histories together
    """

    def __init__(self, repository: Repository, console: Console):
        self._repository = repository
        self._console = console

    def __call__(self, ref_name: str):
        pass
