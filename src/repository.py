import os
from pathlib import Path

from database.database import Database
from util.constant import GITOY_DB_FILE, GITOY_DIR


class Repository:
    def __init__(self, database: Database):
        self.db = database
        self.gitoy_dir = Path(os.getcwd(), GITOY_DIR)
        self.gitoy_db_file = Path(self.gitoy_dir, GITOY_DB_FILE)

    def is_initialized(self):
        return self.gitoy_dir.exists() and self.db.is_initialized()

    def init(self):
        self.gitoy_dir.mkdir(parents=True, exist_ok=True)
        self.db.init()
        self.db.create_main_branch()

    def list_branches(self):
        return self.db.list_branches()