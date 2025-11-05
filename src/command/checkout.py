from repository.repository import Repository
from util.console import Console


class Checkout:
    """
    gitoy-checkout - Switch branches or restore working tree files
    """

    def __init__(self, repository: Repository, console: Console):
        self._repository = repository
        self._console = console

    def __call__(self, ref_name: str):
        pass
