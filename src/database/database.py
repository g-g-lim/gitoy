from database.sqlite import SQLite
from database.entity.blob import Blob
from database.entity.commit import Commit
from database.entity.ref import Ref
from database.entity.reflog import Reflog
from database.entity.tag import Tag
from database.entity.tree import Tree
from database.entity.tree_entry import TreeEntry
from database.entity.index_entry import IndexEntry


class Database: 

    def __init__(self, sqlite: SQLite):
        self.sqlite = sqlite
        self.entity_list = [
            Blob,
            Commit,
            Ref,
            Reflog,
            Tag,
            Tree,
            TreeEntry,
            IndexEntry,
        ]

    def is_initialized(self):
        return self.sqlite.gitoy_db_path.exists() and len(self.sqlite.list_tables()) == len(self.entity_list)


    def init(self):
        for entity in self.entity_list:
            self.sqlite.create_table(entity.table_name(), entity.columns())