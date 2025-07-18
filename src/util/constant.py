from enum import Enum

GITOY_DIR = '.gitoy'
GITOY_DB_FILE = 'gitoy.db'

class GitoyMessage(Enum):
    REPOSITORY_ALREADY_INITIALIZED = 'Gitoy Repository already initialized'
    REPOSITORY_INITIALIZED = 'Gitoy Repository initialized'