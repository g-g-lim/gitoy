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

    def test_find_paths_with_normal_file(self, worktree, temp_file):
        result = worktree.find_paths(temp_file)
        assert len(result) == 1
        assert result[0].name == temp_file
        assert result[0].is_file()
        assert result[0].is_absolute()

    def test_find_paths_with_not_exists_file(self, worktree):
        result = worktree.find_paths('testfile')
        assert len(result) == 0

    def test_find_paths_with_file_in_directory(self, worktree, temp_directory):
        _, path = tempfile.mkstemp(dir=temp_directory)
        result = worktree.find_paths('./' + temp_directory.name)
        assert result is not None
        assert len(result) == 1
        assert result[0].name == (temp_directory / Path(path)).name

        result = worktree.find_paths(temp_directory.name + '/')
        assert result is not None
        assert len(result) == 1

        _, path2 = tempfile.mkstemp(dir=temp_directory)
        result = worktree.find_paths(temp_directory.name + '/')
        assert result is not None
        assert len(result) == 2

        result = worktree.find_paths(temp_directory.name)
        assert result is not None
        assert len(result) == 2
        for path in result:
            assert path.name in [(temp_directory / Path(path)).name, (temp_directory / Path(path2)).name]

        result = worktree.find_paths(temp_directory.name + '/*')
        assert len(result) == 2
        for path in result:
            assert path.name in [(temp_directory / Path(path)).name, (temp_directory / Path(path2)).name]

    def test_find_paths_with_no_file_in_directory_path(self, worktree, temp_directory):
        result = worktree.find_paths(temp_directory.name)
        assert len(result) == 0

        result = worktree.find_paths('./' + temp_directory.name)
        assert len(result) == 0

        result = worktree.find_paths(temp_directory.name + '/*')
        assert len(result) == 0

        result = worktree.find_paths(temp_directory.name + '/')
        assert len(result) == 0

    def test_find_paths_with_subdirectory(self, worktree, temp_directory):
        subdir = temp_directory / "subdir"
        subdir.mkdir(parents=True, exist_ok=True)
        result = worktree.find_paths(temp_directory.name)
        assert len(result) == 0

        file_subdir = subdir / "testfile"
        file_subdir.touch()
        result = worktree.find_paths(temp_directory.name)
        assert len(result) == 1
        assert result[0].name == file_subdir.name

        result = worktree.find_paths(temp_directory.name + '/' + subdir.name + '/' + 'testfile')
        assert len(result) == 1
        assert result[0].name == file_subdir.name

        file2_subdir = subdir / "testfile2"
        file2_subdir.touch()
        result = worktree.find_paths(temp_directory.name)
        assert len(result) == 2
        for path in result:
            assert path.name in [file_subdir.name, file2_subdir.name]

        result = worktree.find_paths(temp_directory.name + '/' + subdir.name)
        assert len(result) == 2
        for path in result:
            assert path.name in [file_subdir.name, file2_subdir.name]

    def test_file_paths_with_dot_path(self, worktree, temp_directory):
        _, path = tempfile.mkstemp(dir=temp_directory)
        result = worktree.find_paths('.')
        assert len(result) == 1
        assert result[0].name == path

        # result = worktree.find_paths('./')
        # assert len(result) == 0
