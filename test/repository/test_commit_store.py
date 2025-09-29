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

    def test_list_commit_logs(self, commit_store: CommitStore, repository: Repository):
        repository.init()
        commit = commit_store.save_commit("ref_tree_id", "commit message")
        commit2 = commit_store.save_commit("ref_tree_id2", "commit message 2", commit)
        commit3 = commit_store.save_commit("ref_tree_id3", "commit message 3", commit2)

        commit_logs = commit_store.list_commit_logs(commit3.object_id)
        assert commit_logs[0].object_id == commit3.object_id
        assert commit_logs[1].object_id == commit2.object_id
        assert commit_logs[2].object_id == commit.object_id
