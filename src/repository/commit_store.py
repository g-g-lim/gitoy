from datetime import datetime
import hashlib
from typing import Optional
from database.database import Database
from database.entity.commit import Commit
from database.entity.commit_parent import CommitParent


class CommitStore:
    def __init__(self, database: Database):
        self.database = database

    # TODO: config 구현 후 계정 정보 조회 기능 추가 설정
    def save_commit(
        self, ref_tree_id: str, message: str, parent_commit: Optional[Commit] = None
    ) -> Commit:
        commit_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_data = {
            "tree_id": ref_tree_id,
            "author_name": "",
            "author_email": "",
            "author_date": commit_datetime,
            "committer_name": "",
            "committer_email": "",
            "committer_date": commit_datetime,
            "message": message,
            "created_at": commit_datetime,
        }
        hash_data = "\n".join(commit_data.values())
        hash_data.encode()
        sha1 = hashlib.sha1()
        sha1.update(hash_data.encode())
        commit_data["object_id"] = sha1.hexdigest()
        new_commit = Commit(**commit_data)
        if parent_commit is not None:
            commit_parent = CommitParent(
                new_commit.object_id, parent_commit.object_id, 0
            )
            self.database.create_commit_parent(commit_parent)
        return self.database.create_commit(new_commit)

    # TODO 2개 이상의 parent 에 대한 처리
    def list_commit_logs(self, commit_object_id: str) -> list[Commit]:
        current = self.database.get_commit(commit_object_id)
        if current is None:
            return []
        commits: list[Commit] = [current]
        while current:
            parents = self.database.get_commit_parents(current.object_id)
            if not parents:
                break
            parent = parents[0]
            current = self.database.get_commit(parent.parent_id)
            if current is not None:
                commits.append(current)

        return commits
