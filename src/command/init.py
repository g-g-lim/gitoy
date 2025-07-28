from repository.repository import Repository
from util.console import Console


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
            self._console.info('Gitoy Repository already initialized')
        else:
            repo_dir = self._repository.init()
            self._console.success(f'Gitoy Repository initialized at {repo_dir.absolute()}')