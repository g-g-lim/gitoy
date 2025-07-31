"""
Test suite for Worktree class.

Tests all Worktree methods including find_paths.
"""
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

from repository.repository import Repository

from src.repository.worktree import Worktree
from src.util.file import File

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


class TestWorktreeFindPaths:
    """Test cases for Repository add method."""

    def test_find_paths_with_normal_file(self, repository: Repository, worktree: Worktree, test_directory: Path, test_file: File):
        repository.init()

        with patch('os.getcwd', return_value=test_directory.as_posix()):
            result = worktree.match(test_file.path.name)
            assert len(result) == 1
            assert result[0].name == test_file.path.name
            assert result[0].is_file()
            assert result[0].is_absolute()

    def test_find_paths_with_not_exists_file(self, repository: Repository, worktree: Worktree, test_root_directory: Path):
        repository.init()

        with patch('os.getcwd', return_value=test_root_directory.as_posix()):
            result = worktree.match('testfile')
            assert len(result) == 0

    def test_find_paths_with_file_in_directory(self, repository: Repository, worktree: Worktree, test_directory: Path):
        repository.init()

        with patch('os.getcwd', return_value=test_directory.parent.as_posix()):
            _, path = tempfile.mkstemp(dir=test_directory)
            result = worktree.match('./' + test_directory.name)
            assert len(result) == 1
            assert result[0].name == (test_directory / Path(path)).name

            result = worktree.match(test_directory.name + '/')
            assert len(result) == 1

            _, path2 = tempfile.mkstemp(dir=test_directory)
            result = worktree.match(test_directory.name + '/')
            assert len(result) == 2

            result = worktree.match(test_directory.name)
            assert len(result) == 2

            result = worktree.match(test_directory.name + '/' + Path(path2).name)
            assert len(result) == 1
            assert result[0].name == (test_directory / Path(path2)).name

    def test_find_paths_with_no_file_in_directory_path(self, repository: Repository, worktree: Worktree, test_directory: Path, test_root_directory: Path):
        repository.init()

        with patch('os.getcwd', return_value=test_root_directory.as_posix()):
            result = worktree.match(test_directory.name)
            assert len(result) == 0

            result = worktree.match('./' + test_directory.name)
            assert len(result) == 0

            result = worktree.match(test_directory.name)
            assert len(result) == 0

            result = worktree.match(test_directory.name + '/')
            assert len(result) == 0

    def test_find_paths_with_subdir(self, repository: Repository, worktree: Worktree, test_directory: Path, test_root_directory: Path):
        repository.init()
        
        subdir = test_directory / "subdir"
        subdir.mkdir(parents=True, exist_ok=True)
        with patch('os.getcwd', return_value=test_root_directory.as_posix()):
            result = worktree.match(test_directory.name)
            assert len(result) == 0

            file_subdir = subdir / "testfile"
            file_subdir.touch()
            result = worktree.match(test_directory.name)
            assert len(result) == 1
            assert result[0].name == file_subdir.name

            result = worktree.match(test_directory.name + '/' + subdir.name + '/' + 'testfile')
            assert len(result) == 1
            assert result[0].name == file_subdir.name

            file2_subdir = subdir / "testfile2"
            file2_subdir.touch()
            result = worktree.match(test_directory.name)
            assert len(result) == 2
            for path in result:
                assert path.name in [file_subdir.name, file2_subdir.name]

            result = worktree.match(test_directory.name + '/' + subdir.name)
            assert len(result) == 2
            for path in result:
                assert path.name in [file_subdir.name, file2_subdir.name]

    def test_file_paths_with_dot_path(self, repository: Repository, worktree: Worktree, test_directory: Path, test_root_directory: Path):
        repository.init()

        with patch('os.getcwd', return_value=test_directory.as_posix()):
            _, path = tempfile.mkstemp(dir=test_directory)

            # test/test_directory/test_file
            result = worktree.match('.')
            assert len(result) == 1
            assert result[0].is_file()
            assert result[0].name == (test_directory / Path(path)).name

            result = worktree.match('./')
            assert len(result) == 1
            assert result[0].is_file()
            assert result[0].name == (test_directory / Path(path)).name


        subdir = test_directory / "subdir"
        subdir.mkdir(parents=True, exist_ok=True)

        with patch('os.getcwd', return_value=subdir.as_posix()):
            result = worktree.match('.')
            assert len(result) == 0

            result = worktree.match('./')
            assert len(result) == 0

            # test/test_directory/subdir/testfile
            file_subdir = subdir / "testfile"
            file_subdir.touch()

            result = worktree.match('.')
            assert len(result) == 1
            
            result = worktree.match('./')
            assert len(result) == 1
            assert result[0].is_file()
            assert result[0].name == file_subdir.name

        with patch('os.getcwd', return_value=test_directory.as_posix()):
            # test/test_directory/
            result = worktree.match('.')
            assert len(result) == 2

    def test_file_paths_with_parent_dot_path(self, repository: Repository, worktree: Worktree, test_directory: Path, test_root_directory: Path):
        repository.init()

        subdir = test_directory / "subdir"
        subdir.mkdir(parents=True, exist_ok=True)

        with patch('os.getcwd', return_value=subdir.as_posix()):
            # test/test_directory/subdir/testfile
            file_subdir = subdir / "testfile"
            file_subdir.touch()

            result = worktree.match('..')
            assert len(result) == 1

            # test/test_directory/test_file
            _, path = tempfile.mkstemp(dir=test_directory)
            result = worktree.match('..')
            assert len(result) == 2
            for path in result:
                assert path.name in [file_subdir.name, (test_directory / Path(path)).name]

            result = worktree.match('../')
            assert len(result) == 2