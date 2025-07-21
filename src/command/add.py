from repository import Repository
from util.console import Console

class Add: 

    """
    gitoy-add - Add file contents to the index
    """

    def __init__(self, repository: Repository, console: Console):
        self.repository = repository
        self.console = console

    def __call__(self, add_paths: list[str]):
        self.repository.add_to_index(add_paths)