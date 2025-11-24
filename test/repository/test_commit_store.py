from repository.repository import Repository


class TestCommitStore:
    def test_save_commit(
        self, repository: Repository,
    ):
        repository.init()
        commit = repository.commit_store.save_commit("ref_tree_id", "commit message")
        commit_db = repository.database.get_commit(commit.object_id)
        assert commit_db is not None
        assert commit_db.message == "commit message"
        assert commit_db.generation_number == 0

    def test_save_commit_with_parent(
        self, repository: Repository
    ):
        repository.init()
        parent_commit = repository.commit_store.save_commit("ref_tree_id", "commit message")
        _child_commit = repository.commit_store.save_commit("ref_tree_id2", "commit message 2", parent_commit)
        child_commit = repository.database.get_commit(_child_commit.object_id)
        
        assert child_commit is not None
        assert child_commit.generation_number == 1
        
        commit_children = repository.database.get_commit_children(parent_commit.object_id)
        assert commit_children is not None
        assert len(commit_children) == 1
        assert commit_children[0].parent_id == parent_commit.object_id

    def test_list_commit_logs(self, repository: Repository):
        repository.init()
        commit = repository.commit_store.save_commit("ref_tree_id", "commit message")
        commit2 = repository.commit_store.save_commit("ref_tree_id2", "commit message 2", commit)
        commit3 = repository.commit_store.save_commit("ref_tree_id3", "commit message 3", commit2)

        commit_logs = repository.commit_store.list_commit_logs(commit3.object_id)
        assert commit_logs[0].object_id == commit3.object_id
        assert commit_logs[1].object_id == commit2.object_id
        assert commit_logs[2].object_id == commit.object_id

    # TODO merge commit generation test
    def test_generation_number(self, repository: Repository):
        """
          A(0)--B(1)--C(2)------G(5)--H(6)
                \             /
                D(2)--E(3)--F(4)
        """
        pass
