from dataclasses import dataclass


from database.entity.entity import Entity


@dataclass
class CommitParent(Entity):
    """
    Parent relationship for Git commits

    Attributes:
        commit_id: Child commit object_id (part of composite primary key)
        parent_id: Parent commit object_id (part of composite primary key)
        parent_order: Order of parent (for merge commits)
    """

    commit_id: str  # Primary key component
    parent_id: str  # Primary key component
    parent_order: int

    @staticmethod
    def table_name():
        return "commit_parent"

    @staticmethod
    def columns():
        return [
            "commit_id TEXT",
            "parent_id TEXT",
            "parent_order INTEGER",
        ]
