from pathlib import Path
import tempfile
from unittest.mock import patch
from src.repository.repo_path import RepositoryPath


class TestRepositoryPath:
    """Test cases for Repository class."""

    def test_absolute_path_to_relative_path(
        self, repository_path: RepositoryPath, test_file_path: Path
    ):
        # /{absolute_path}/gitoy-2/test/test_dir/tmp3d909r0g
        repository_path.create_repo_dir()
        relative_path = repository_path.to_relative_path(test_file_path.absolute())
        assert relative_path == test_file_path.relative_to(
            repository_path.worktree_path
        )
        assert relative_path.is_absolute() is False

    def test_absolute_path_to_relative_path_2(
        self, repository_path: RepositoryPath, test_directory: Path
    ):
        # /{absolute_path}/gitoy-2/test/test_dir/tmp3d909r0g
        repository_path.create_repo_dir()
        relative_path = repository_path.to_relative_path(test_directory.absolute())
        assert relative_path == test_directory.relative_to(
            repository_path.worktree_path
        )
        assert relative_path.is_absolute() is False

    def test_invalid_path(self, repository_path: RepositoryPath):
        pass

    def test_relative_path_to_relative_path(
        self,
        repository_path: RepositoryPath,
        test_directory: Path,
        test_file_path: Path,
    ):
        # path: tmp3d909r0g current_dir: test/test_dir
        repository_path.create_repo_dir()

        with patch("os.getcwd", return_value=test_directory.as_posix()):
            relative_path = repository_path.to_relative_path(test_file_path.name)
            assert relative_path == test_file_path.relative_to(
                repository_path.worktree_path
            )

    def test_relative_path_to_relative_path_2(
        self, repository_path: RepositoryPath, test_directory: Path
    ):
        # path: ./ current_dir: test/test_dir
        repository_path.create_repo_dir()

        with patch("os.getcwd", return_value=test_directory.as_posix()):
            relative_path = repository_path.to_relative_path("./")
            assert relative_path == Path(test_directory.name)
            assert relative_path.as_posix() == test_directory.name

    def test_relative_path_to_relative_path_3(
        self, repository_path: RepositoryPath, test_directory: Path
    ):
        # path: ../ current_dir: test/test_dir/sub_dir
        repository_path.create_repo_dir()

        sub_dir = test_directory / "sub_dir"
        sub_dir.mkdir(parents=True, exist_ok=True)

        with patch("os.getcwd", return_value=sub_dir.as_posix()):
            relative_path = repository_path.to_relative_path("../")
            assert relative_path == Path(test_directory.name)
            assert relative_path.as_posix() == test_directory.name

        with patch("os.getcwd", return_value=test_directory.as_posix()):
            relative_path = repository_path.to_relative_path("sub_dir")
            assert relative_path == Path("test_dir/sub_dir")
            assert relative_path.as_posix() == "test_dir/sub_dir"

            relative_path = repository_path.to_relative_path("./sub_dir")
            assert relative_path == Path("test_dir/sub_dir")

    def test_relative_path_to_relative_path_4(
        self, repository_path: RepositoryPath, test_directory: Path
    ):
        # path: ../ current_dir: test/test_dir/sub_dir/temp_file
        repository_path.create_repo_dir()
        sub_dir = test_directory / "sub_dir"
        sub_dir.mkdir(parents=True, exist_ok=True)

        _, path = tempfile.mkstemp(dir=sub_dir)
        temp_file_path = Path(path)

        with patch("os.getcwd", return_value=test_directory.as_posix()):
            relative_path = repository_path.to_relative_path(
                f"./sub_dir/{temp_file_path.name}"
            )
            assert relative_path == Path(
                f"{test_directory.name}/sub_dir/{temp_file_path.name}"
            )
            assert (
                relative_path.as_posix()
                == f"{test_directory.name}/sub_dir/{temp_file_path.name}"
            )

            relative_path = repository_path.to_relative_path(
                f"sub_dir/{temp_file_path.name}"
            )
            assert relative_path == Path(
                f"{test_directory.name}/sub_dir/{temp_file_path.name}"
            )

        with patch("os.getcwd", return_value=sub_dir.as_posix()):
            relative_path = repository_path.to_relative_path(temp_file_path.name)
            assert relative_path == Path(
                f"{test_directory.name}/sub_dir/{temp_file_path.name}"
            )
            assert (
                relative_path.as_posix()
                == f"{test_directory.name}/sub_dir/{temp_file_path.name}"
            )

            relative_path = repository_path.to_relative_path("./" + temp_file_path.name)
            assert relative_path == Path(
                f"{test_directory.name}/sub_dir/{temp_file_path.name}"
            )

            relative_path = repository_path.to_relative_path(
                "../sub_dir/" + temp_file_path.name
            )
            assert relative_path == Path(
                f"{test_directory.name}/sub_dir/{temp_file_path.name}"
            )

    def test_relative_path_to_relative_path_5(
        self, repository_path: RepositoryPath, test_directory: Path
    ):
        # path: ./ current_dir: test/test_dir
        repository_path.create_repo_dir()

        with patch("os.getcwd", return_value=test_directory.parent.as_posix()):
            relative_path = repository_path.to_relative_path("./")
            assert relative_path == Path(".")
            assert relative_path.as_posix() == "."

        with patch("os.getcwd", return_value=test_directory.as_posix()):
            relative_path = repository_path.to_relative_path("../")
            assert relative_path == Path(".")
