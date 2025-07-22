"""
Test suite for Worktree class.

Tests all Worktree methods including find_paths, read_file, write_file.
"""
from pathlib import Path
import sys
import tempfile

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


class TestWorktreeFindPaths:
    """Test cases for Repository add method."""

    def test_find_paths_with_normal_file(self, repository, temp_file):
        result = repository.worktree.find_paths(temp_file)
        assert result is not None
        assert len(result) == 1
        assert result[0].name == temp_file

    def test_find_paths_with_not_exists_file(self, repository):
        result = repository.worktree.find_paths('testfile')
        assert result is not None
        assert len(result) == 0
    
    def test_find_paths_with_directory_path(self, repository, temp_directory):
        result = repository.worktree.find_paths(temp_directory.name)
        assert result is not None
        assert len(result) == 0

    def test_find_paths_with_file_in_directory(self, repository, temp_directory):
        tempfile.mkstemp(dir=temp_directory)
        result = repository.worktree.find_paths(temp_directory.name)
        assert result is not None
        assert len(result) == 1