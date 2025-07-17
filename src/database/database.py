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

    def init(self):
        entity_list = [
            Blob,
            Commit,
            Ref,
            Reflog,
            Tag,
            Tree,
            TreeEntry,
            IndexEntry,
        ]

        for entity in entity_list:
            self.sqlite.create_table(entity.table_name(), entity.columns())