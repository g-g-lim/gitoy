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
        self.repository.init()
        self.console.info(GitoyMessage.REPOSITORY_INITIALIZED)