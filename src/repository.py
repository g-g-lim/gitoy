import os
from pathlib import Path

from database.database import Database
from util.constant import GITOY_DIR, GitoyMessage


class Repository:
    def __init__(self, database: Database):
        self.db = database

    def init(self):
        gitoy_dir = Path(os.getcwd(), GITOY_DIR)
        if not gitoy_dir.exists():
            gitoy_dir.mkdir(parents=True, exist_ok=True)
        self.db.init()

    def add(self, file: str):
        pass