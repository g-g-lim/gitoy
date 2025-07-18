GITOY_DIR = '.gitoy'
GITOY_DB_FILE = 'gitoy.db'

from enum import Enum

class GitoyMessage(Enum):
    REPOSITORY_ALREADY_INITIALIZED = 'Gitoy Repository already initialized'
    REPOSITORY_INITIALIZED = 'Gitoy Repository initialized'