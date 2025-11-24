from datetime import datetime
import hashlib
from typing import Optional
from database.database import Database
from database.entity.commit import Commit
from database.entity.commit_parent import CommitParent


class CommitStore:
    def __init__(self, database: Database):
        self.database = database
        
    def _hash(self, commit_data: dict):
        hash_data = "\n".join(map(str, commit_data.values()))
        hash_data.encode()
        sha1 = hashlib.sha1()
        sha1.update(hash_data.encode())
        commit_data["object_id"] = sha1.hexdigest()
        return commit_data

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
            "generation": 0 if parent_commit is None else parent_commit.generation + 1
        }
        
        commit_data = self._hash(commit_data)
        new_commit = Commit(**commit_data)
        
        if parent_commit is not None:
            commit_parent = CommitParent(
                new_commit.object_id, parent_commit.object_id, 0
            )
            self.database.create_commit_parent(commit_parent)
        return self.database.create_commit(new_commit)
    
    def save_merge_commit(self, ref_tree_id: str,parent_commits: list[Commit],  message: Optional[str] = None) -> Commit:
        commit_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        generation = max([p.generation for p in parent_commits]) + 1
        if message is None:
            message = 'Merge commit'
            
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
            "generation": generation
        }
        
        commit_data = self._hash(commit_data)
        new_commit = Commit(**commit_data)
        
        for p in parent_commits:
            commit_parent = CommitParent(
                new_commit.object_id, p.object_id, 0
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
    
    def get_commit_parents(self, commit_object_id: str): 
        parents = self.database.get_commit_parents(commit_object_id)
        parent_ids = [p.parent_id for p in parents] 
        return self.database.list_commits(parent_ids)
        

