"""
Test suite for Repository class.

Tests all Repository methods including initialization, branch management,
error handling, and edge cases.
"""
import hashlib
from pathlib import Path
import tempfile
from unittest.mock import patch
import sys

from src.repository import Repository

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


class TestRepositoryInit:
    """Test cases for Repository class."""

    def test_init_repository(self, repository: Repository):
        """Test repository initialization check when both file system and database are initialized."""
        repository.init()
        result = repository.is_initialized()
        
        assert result is True
        assert repository.path.repo_dir is not None
        assert repository.path.get_repo_db_path() is not None

    def test_init_repository_with_existing_repo(self, repository: Repository):
        """Test repository initialization check when both file system and database are initialized."""
        result = repository.is_initialized()
        
        assert result is True
        assert repository.path.repo_dir is not None
        assert repository.path.get_repo_db_path() is not None


class TestRepositoryBranch:
    """Test cases for Repository branch management."""

    def test_list_branches(self, repository: Repository):
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

    def test_create_branch_when_no_initial_commit_exists(self, repository: Repository):
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

    def test_create_branch_with_same_name(self, repository: Repository):
        """Test creating a new branch with same name."""
        result = repository.create_branch("test_branch")
        
        assert result.success is False
        assert result.error == "Branch refs/heads/test_branch already exists"

    # def test_create_branch_when_initial_commit_exists(self, repository):
    #     """Test creating a new branch when initial commit exists."""
    #     raise NotImplementedError()

    def test_update_head_branch(self, repository: Repository):
        """Test updating head branch."""
        result = repository.update_head_branch("test_branch_1")

        assert result.success is True
        assert result.value.ref_name == "refs/heads/test_branch_1"
        assert result.value.head == 1
        assert result.value.target_object_id is None
        assert result.value.ref_type == "branch"
        assert result.value.is_symbolic == 0
        assert result.value.symbolic_target is None

    def test_update_head_branch_with_same_name(self, repository: Repository):
        """Test updating head branch with same name."""
        result = repository.update_head_branch("test_branch_1")

        assert result.success is False
        assert result.error == "Branch refs/heads/test_branch_1 already exists"
    
    # def test_delete_branch(self, repository):
    #     raise NotImplementedError()

    def test_delete_branch_when_not_exists_branch(self, repository: Repository):
        result = repository.delete_branch("test_branch_2")
        assert result.success is False
        assert result.error == "Branch refs/heads/test_branch_2 not found"

    def test_delete_branch_with_head_branch(self, repository: Repository):
        result = repository.delete_branch("test_branch_1")
        assert result.success is False
        assert result.error == "Branch refs/heads/test_branch_1 is the head branch"

class TestRepositoryAddToIndex:
    """Test cases for Repository add to index."""

    def test_add_to_index_with_not_in_repository(self, repository: Repository):
        result = repository.add_to_index(["test_file"])
        assert result.success is False
        assert result.error == "Not in a repository"

    def test_add_to_index_with_not_exists_file(self, repository: Repository, test_directory: Path):
        with patch('pathlib.Path.cwd') as mock_cwd:
            mock_cwd.return_value = test_directory

            result = repository.add_to_index(["temp_file"])
            assert result.success is False
            assert result.error == "Pathspec temp_file did not match any files"

    def test_add_to_index_with_exists_file(self, repository: Repository, test_file: Path):
        with patch('pathlib.Path.cwd') as mock_cwd:
            mock_cwd.return_value = test_file.parent

            result = repository.add_to_index([test_file.name])

            assert result.success is True

class TestRepositoryHashObject:
    """Test cases for Repository hash object."""

    def test_hash_file_with_normal_file(self, repository: Repository, test_file: Path):
        result = repository.hash_file(test_file)

        sha1 = hashlib.sha1()
        sha1.update(test_file.read_bytes())

        assert result.success is True
        assert len(result.value) == 40
        assert result.value == sha1.hexdigest()

        test_file.write_bytes(b"append_data")
        result = repository.hash_file(test_file)

        sha2= hashlib.sha1()
        sha2.update(test_file.read_bytes())

        assert result.success is True
        assert len(result.value) == 40
        assert result.value == sha2.hexdigest()
        assert sha1.hexdigest() != sha2.hexdigest()

    def test_hash_file_with_empty_file(self, repository: Repository):
        _, path = tempfile.mkstemp()
        empty_file = Path(path)
        result = repository.hash_file(empty_file)

        sha1 = hashlib.sha1()
        sha1.update(b"")

        assert result.success is True
        assert len(result.value) == 40
        assert result.value == sha1.hexdigest()

    def test_hash_file_with_same_content_but_different_path(self, repository: Repository, test_file: Path):
        _, path = tempfile.mkstemp()
        test_file2 = Path(path)
        test_file2.write_bytes(test_file.read_bytes())

        assert repository.hash_file(test_file).value == repository.hash_file(test_file2).value
    
    def test_hash_file_with_large_file(self, repository: Repository, test_large_file: Path):
        result = repository.hash_file(test_large_file)

        sha1 = hashlib.sha1()
        sha1.update(test_large_file.read_bytes())

        assert result.success is True
        assert len(result.value) == 40
        assert result.value == sha1.hexdigest()

    def test_hash_file_with_binary_file(self, repository: Repository):
        fd, path = tempfile.mkstemp()
        binary_file = Path(path)
        binary_file.write_bytes(b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F")
        result = repository.hash_file(binary_file)

        sha1 = hashlib.sha1()
        sha1.update(binary_file.read_bytes())

        assert result.success is True
        assert len(result.value) == 40
        assert result.value == sha1.hexdigest()

    def test_hash_file_with_not_exists_file(self, repository: Repository):
        result = repository.hash_file(Path("not_exists_file"))
        assert result.success is False
        assert result.error == "File not_exists_file not found"

    def test_hash_file_with_image_file(self, repository: Repository, test_image_file: Path):
        result = repository.hash_file(test_image_file)

        sha1 = hashlib.sha1()
        sha1.update(test_image_file.read_bytes())

        assert result.success is True
        assert len(result.value) == 40
        assert result.value == sha1.hexdigest()
        