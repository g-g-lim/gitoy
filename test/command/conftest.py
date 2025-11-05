from command.status import Status
from command.init import Init
import pytest
from repository.repository import Repository
from util.console import Console


@pytest.fixture(scope="function")
def console():
    return Console()


@pytest.fixture(scope="function")
def init_command(repository: Repository, console: Console):
    return Init(repository, console)


@pytest.fixture(scope="function")
def status_command(repository: Repository, console: Console):
    return Status(repository, console)
