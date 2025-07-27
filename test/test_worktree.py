"""
Test suite for Worktree class.

Tests all Worktree methods including find_paths.
"""
from pathlib import Path
import sys
import tempfile

from src.repository.worktree import Worktree

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


class TestWorktreeFindPaths:
    """Test cases for Repository add method."""

    def test_find_paths_with_normal_file(self, worktree: Worktree, test_file: Path):
        result = worktree.find_files(test_file.name, test_file.parent)
        assert len(result) == 1
        assert result[0].path.name == test_file.name
        assert result[0].path.is_file()
        assert result[0].path.is_absolute()

    def test_find_paths_with_not_exists_file(self, worktree: Worktree):
        result = worktree.find_files('testfile')
        assert len(result) == 0

    def test_find_paths_with_file_in_directory(self, worktree: Worktree, test_directory: Path, test_root_directory: Path):
        _, path = tempfile.mkstemp(dir=test_directory)
        result = worktree.find_files('./' + test_directory.name, test_root_directory)
        assert result is not None
        assert len(result) == 1
        assert result[0].path.name == (test_directory / Path(path)).name

        result = worktree.find_files(test_directory.name + '/', test_root_directory)
        assert result is not None
        assert len(result) == 1

        _, path2 = tempfile.mkstemp(dir=test_directory)
        result = worktree.find_files(test_directory.name + '/', test_root_directory)
        assert result is not None
        assert len(result) == 2

        result = worktree.find_files(test_directory.name, test_root_directory)
        assert result is not None
        assert len(result) == 2
        for file in result:
            assert file.path.name in [(test_directory / Path(path)).name, (test_directory / Path(path2)).name]

        result = worktree.find_files(test_directory.name + '/*', test_root_directory)
        assert len(result) == 2
        for file in result:
            assert file.path.name in [(test_directory / Path(path)).name, (test_directory / Path(path2)).name]

    def test_find_paths_with_no_file_in_directory_path(self, worktree: Worktree, test_directory: Path, test_root_directory: Path):
        result = worktree.find_files(test_directory.name, test_root_directory)
        assert len(result) == 0

        result = worktree.find_files('./' + test_directory.name, test_root_directory)
        assert len(result) == 0

        result = worktree.find_files(test_directory.name + '/*', test_root_directory)
        assert len(result) == 0

        result = worktree.find_files(test_directory.name + '/', test_root_directory)
        assert len(result) == 0

    def test_find_paths_with_subdirectory(self, worktree: Worktree, test_directory: Path, test_root_directory: Path):
        subdir = test_directory / "subdir"
        subdir.mkdir(parents=True, exist_ok=True)
        result = worktree.find_files(test_directory.name, test_root_directory)
        assert len(result) == 0

        file_subdir = subdir / "testfile"
        file_subdir.touch()
        result = worktree.find_files(test_directory.name, test_root_directory)
        assert len(result) == 1
        assert result[0].path.name == file_subdir.name

        result = worktree.find_files(test_directory.name + '/' + subdir.name + '/' + 'testfile', test_root_directory)
        assert len(result) == 1
        assert result[0].path.name == file_subdir.name

        file2_subdir = subdir / "testfile2"
        file2_subdir.touch()
        result = worktree.find_files(test_directory.name, test_root_directory)
        assert len(result) == 2
        for file in result:
            assert file.path.name in [file_subdir.name, file2_subdir.name]

        result = worktree.find_files(test_directory.name + '/' + subdir.name, test_root_directory)
        assert len(result) == 2
        for file in result:
            assert file.path.name in [file_subdir.name, file2_subdir.name]

    def test_file_paths_with_dot_path(self, worktree: Worktree, test_directory: Path, test_root_directory: Path):
        _, path = tempfile.mkstemp(dir=test_directory)

        # test/test_directory/test_file
        result = worktree.find_files('.', test_directory)
        assert len(result) == 1
        assert result[0].path.is_file()
        assert result[0].path.name == (test_directory / Path(path)).name

        result = worktree.find_files('./', test_directory)
        assert len(result) == 1
        assert result[0].path.is_file()
        assert result[0].path.name == (test_directory / Path(path)).name

        # test/test_directory/subdir
        subdir = test_directory / "subdir"
        subdir.mkdir(parents=True, exist_ok=True)
        result = worktree.find_files('.', subdir)
        assert len(result) == 0

        result = worktree.find_files('./', subdir)
        assert len(result) == 0

        # test/test_directory/subdir/testfile
        file_subdir = subdir / "testfile"
        file_subdir.touch()

        result = worktree.find_files('.', subdir)
        assert len(result) == 1
        
        result = worktree.find_files('./', subdir)
        assert len(result) == 1
        assert result[0].path.is_file()
        assert result[0].path.name == file_subdir.name

        # test/test_directory/
        result = worktree.find_files('.', test_directory)
        assert len(result) == 2

    def test_file_paths_with_parent_dot_path(self, worktree: Worktree, test_directory: Path, test_root_directory: Path):
        # test/test_directory/subdir/testfile
        subdir = test_directory / "subdir"
        subdir.mkdir(parents=True, exist_ok=True)
        file_subdir = subdir / "testfile"
        file_subdir.touch()

        result = worktree.find_files('..', subdir)
        assert len(result) == 1

        # test/test_directory/test_file
        _, path = tempfile.mkstemp(dir=test_directory)
        result = worktree.find_files('..', subdir)
        assert len(result) == 2
        for file in result:
            assert file.path.name in [file_subdir.name, (test_directory / Path(path)).name]

        result = worktree.find_files('../', subdir)
        assert len(result) == 2