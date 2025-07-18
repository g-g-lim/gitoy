from repository import Repository
from util.console import Console
from util.constant import INITIALIZED_MESSAGE, REPOSITORY_ALREADY_INITIALIZED


class Init:
    """
    Initialize a new Gitoy repository
    """

    def __init__(self, repository: Repository, console: Console):
        self.repository = repository
        self.console = console

    def __call__(self):
        is_initialized = self.repository.is_initialized()
        if is_initialized:
            self.console.info(REPOSITORY_ALREADY_INITIALIZED)
        else:
            repo_dir = self.repository.init()
            self.console.success(INITIALIZED_MESSAGE(repo_dir.absolute()))