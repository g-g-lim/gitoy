from repository import Repository
from util.console import Console
from util.constant import GitoyMessage


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
            self.console.info(GitoyMessage.REPOSITORY_ALREADY_INITIALIZED)
        else:
            self.repository.init()
            self.console.success(GitoyMessage.REPOSITORY_INITIALIZED)