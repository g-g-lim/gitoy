"""
Test suite for Repository class.

Tests all Repository methods including initialization, branch management,
error handling, and edge cases.
"""
from pathlib import Path
import sys

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


class TestRepositoryInit:
    """Test cases for Repository class."""

    def test_init_repository(self, repository):
        """Test repository initialization check when both file system and database are initialized."""
        repository.init()
        result = repository.is_initialized()
        
        assert result is True
        assert repository.path.repo_dir.exists()
        assert repository.path.get_repo_db_path().exists()  

    def test_init_repository_with_existing_repo(self, repository):
        """Test repository initialization check when both file system and database are initialized."""
        result = repository.is_initialized()
        
        assert result is True
        assert repository.path.repo_dir.exists()
        assert repository.path.get_repo_db_path().exists()  


class TestRepositoryBranch:
    """Test cases for Repository branch management."""

    def test_list_branches(self, repository):
        """Test listing all branches."""
        result = repository.list_branches()
        head_branch = result[0]
        
        assert head_branch.ref_name == "refs/heads/main"
        assert head_branch.head == 1
        assert head_branch.target_object_id is None
        assert head_branch.ref_type == "branch"
        assert head_branch.is_symbolic == 0
        assert head_branch.symbolic_target is None
        assert head_branch.namespace is None
        assert head_branch.updated_at is not None

    def test_create_branch_when_no_initial_commit_exists(self, repository):
        """Test creating a new branch when no initial commit exists."""
        result = repository.create_branch("test_branch")
        
        assert result.success is True
        assert result.value['new'] is False

        create_ref = result.value['ref']

        assert create_ref.ref_name == "refs/heads/test_branch"
        assert create_ref.head == 1
        assert create_ref.target_object_id is None
        assert create_ref.ref_type == "branch"
        assert create_ref.is_symbolic == 0
        assert create_ref.symbolic_target is None

    def test_create_branch_with_same_name(self, repository):
        """Test creating a new branch with same name."""
        result = repository.create_branch("test_branch")
        
        assert result.success is False
        assert result.error == "Branch refs/heads/test_branch already exists"

    def test_create_branch_when_initial_commit_exists(self, repository):
        """Test creating a new branch when initial commit exists."""
        raise NotImplementedError()

    def test_update_head_branch(self, repository):
        """Test updating head branch."""
        result = repository.update_head_branch("test_branch_1")

        assert result.success is True
        assert result.value.ref_name == "refs/heads/test_branch_1"
        assert result.value.head == 1
        assert result.value.target_object_id is None
        assert result.value.ref_type == "branch"
        assert result.value.is_symbolic == 0
        assert result.value.symbolic_target is None

    def test_update_head_branch_with_same_name(self, repository):
        """Test updating head branch with same name."""
        result = repository.update_head_branch("test_branch_1")

        assert result.success is False
        assert result.error == "Branch refs/heads/test_branch_1 already exists"
    
    def test_delete_branch(self, repository):
        raise NotImplementedError()

    def test_delete_branch_when_not_exists_branch(self, repository):
        result = repository.delete_branch("test_branch_2")
        assert result.success is False
        assert result.error == "Branch refs/heads/test_branch_2 not found"

    def test_delete_branch_with_head_branch(self, repository):
        result = repository.delete_branch("test_branch_1")
        assert result.success is False
        assert result.error == "Branch refs/heads/test_branch_1 is the head branch"