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
        result = self._repository.checkout(ref_name)
        if result.failed:
            self._console.error(result.error)
        else:
            self._console.info(f"Switched to branch '{ref_name}'")
