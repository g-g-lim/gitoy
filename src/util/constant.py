GITOY_DIR = '.gitoy'

from enum import Enum

class GitoyMessage(Enum):
    REPOSITORY_ALREADY_INITIALIZED = 'Gitoy Repository already initialized'
    REPOSITORY_INITIALIZED = 'Gitoy Repository initialized'