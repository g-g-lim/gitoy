from repository.repository import Repository
from util.console import Console
from util.constant import INITIALIZED_MESSAGE, REPOSITORY_ALREADY_INITIALIZED


class Init:
    """
    gitoy-init - Create an empty Git repository
       or reinitialize an existing one
    """

    def __init__(self, repository: Repository, console: Console):
        self._repository = repository
        self._console = console

    def __call__(self):
        is_initialized = self._repository.is_initialized()
        if is_initialized:
            self._console.info(REPOSITORY_ALREADY_INITIALIZED)
        else:
            repo_dir = self._repository.init()
            self._console.success(INITIALIZED_MESSAGE(repo_dir.absolute()))