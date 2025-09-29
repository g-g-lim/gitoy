from database.database import Database
from repository.commit_store import CommitStore
from repository.repository import Repository


class TestCommitStore:
    def test_save_commit(
        self, commit_store: CommitStore, repository: Repository, database: Database
    ):
        repository.init()
        commit = commit_store.save_commit("ref_tree_id", "commit message")
        commit_db = database.get_commit(commit.object_id)
        assert commit_db is not None
        assert commit_db.message == "commit message"

    def test_save_commit_with_parent(
        self, commit_store: CommitStore, repository: Repository, database: Database
    ):
        repository.init()
        parent_commit = commit_store.save_commit("ref_tree_id", "commit message")
        commit_store.save_commit("ref_tree_id2", "commit message 2", parent_commit)
        commit_children = database.get_commit_children(parent_commit.object_id)
        assert commit_children is not None
        assert len(commit_children) == 1
        assert commit_children[0].parent_id == parent_commit.object_id
