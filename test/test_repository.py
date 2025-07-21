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

    def test_init_repository(self, repository, file_handler):
        """Test repository initialization check when both file system and database are initialized."""
        repository.init()
        result = repository.is_initialized()
        
        assert result is True
        assert file_handler.repo_dir.exists()
        assert file_handler.repo_db_file.exists()  

    def test_init_repository_with_existing_repo(self, repository, file_handler):
        """Test repository initialization check when both file system and database are initialized."""
        result = repository.is_initialized()
        
        assert result is True
        assert file_handler.repo_dir.exists()
        assert file_handler.repo_db_file.exists()  


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