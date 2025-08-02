"""
Test suite for Status command.

Tests the Status command output formatting and integration with Repository.
"""
from pathlib import Path
import tempfile
from unittest.mock import patch
from io import StringIO

from command.init import Init
from command.status import Status
from repository.repository import Repository


class TestStatusCommand:
    """Test cases for Status command."""

    def test_status_command_uninitialized_repository(self, status_command: Status):
        """Test status command in uninitialized repository shows error."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            status_command()
            assert "Not a gitoy repository" in mock_stdout.getvalue()

    def test_status_command_empty_repository(self, init_command: Init, status_command: Status):
        """Test status command in empty repository shows branch only."""
        init_command()

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            status_command()
            assert "On branch main" in mock_stdout.getvalue()
            assert "unstaged" not in mock_stdout.getvalue()
            assert "untracked" not in mock_stdout.getvalue()

    def test_status_command_with_untracked_files(self, init_command: Init, status_command: Status, test_directory: Path):
        """Test status command shows untracked files correctly."""
        init_command()

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        
            with patch('os.getcwd', return_value=test_directory.as_posix()):
                _, path1 = tempfile.mkstemp(dir=test_directory)
                path = Path(path1)
                
                status_command()

                assert "On branch main" in mock_stdout.getvalue()
                assert "untracked" in mock_stdout.getvalue()
                assert f"new file: {path.relative_to(test_directory.parent)}" in mock_stdout.getvalue()
                assert "unstaged" not in mock_stdout.getvalue()

    def test_status_command_with_unstaged_files(self, init_command: Init, status_command: Status, repository: Repository, test_directory: Path):
        """Test status command shows unstaged files correctly."""
        init_command()

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        
            with patch('os.getcwd', return_value=test_directory.as_posix()):
                _, path = tempfile.mkstemp(dir=test_directory)
                path = Path(path)
                
                repository.add_index([path.name])
                path.write_bytes(b"modified content")
                
                status_command()
            
                assert "On branch main" in mock_stdout.getvalue()
                assert "unstaged" in mock_stdout.getvalue()
                assert f"modified: {path.relative_to(test_directory.parent)}" in mock_stdout.getvalue()

    def test_status_command_mixed_file_states(self, init_command: Init, status_command: Status, repository: Repository, test_directory: Path):
        """Test status command with multiple file states."""
        init_command()
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            with patch('os.getcwd', return_value=test_directory.as_posix()):
                _, untracked_path = tempfile.mkstemp(dir=test_directory)
                _, modified_path = tempfile.mkstemp(dir=test_directory)
                _, deleted_path = tempfile.mkstemp(dir=test_directory)
                
                untracked_path = Path(untracked_path)
                modified_path = Path(modified_path)
                deleted_path = Path(deleted_path)
                
                repository.add_index([modified_path.name, deleted_path.name])
                modified_path.write_bytes(b"modified content")
                deleted_path.unlink()
                
                status_command()
                
                assert "On branch main" in mock_stdout.getvalue()
                assert "unstaged" in mock_stdout.getvalue()
                assert "untracked" in mock_stdout.getvalue()
                assert f"modified: {modified_path.relative_to(test_directory.parent)}" in mock_stdout.getvalue()
                assert f"deleted: {deleted_path.relative_to(test_directory.parent)}" in mock_stdout.getvalue()
                assert f"new file: {untracked_path.relative_to(test_directory.parent)}" in mock_stdout.getvalue()

    def test_status_command_mixed_file_states_with_root_directory(self, init_command: Init, status_command: Status, repository: Repository, test_directory: Path):
        """Test status command with multiple file states."""
        init_command()
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            with patch('os.getcwd', return_value=test_directory.parent.as_posix()):
                _, untracked_path = tempfile.mkstemp(dir=test_directory)
                _, modified_path = tempfile.mkstemp(dir=test_directory)
                _, deleted_path = tempfile.mkstemp(dir=test_directory)
                
                untracked_path = test_directory / untracked_path
                modified_path = test_directory / modified_path
                deleted_path = test_directory / deleted_path
                
                repository.add_index([
                    modified_path.as_posix(),
                    deleted_path.as_posix(),
                ])
                modified_path.write_bytes(b"modified content")
                deleted_path.unlink()
                
                status_command()
                
                assert "On branch main" in mock_stdout.getvalue()
                assert "unstaged" in mock_stdout.getvalue()
                assert "untracked" in mock_stdout.getvalue()
                assert f"modified: {modified_path.relative_to(test_directory.parent)}" in mock_stdout.getvalue()
                assert f"deleted: {deleted_path.relative_to(test_directory.parent)}" in mock_stdout.getvalue()
                assert f"new file: {untracked_path.relative_to(test_directory.parent)}" in mock_stdout.getvalue()

    def test_status_command_mixed_file_states_with_root_directory_2(self, init_command: Init, status_command: Status, repository: Repository, test_directory: Path):
        """Test status command with multiple file states."""
        init_command()
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            with patch('os.getcwd', return_value=test_directory.as_posix()):
                _, untracked_path = tempfile.mkstemp(dir=test_directory.parent)
                _, modified_path = tempfile.mkstemp(dir=test_directory)
                _, deleted_path = tempfile.mkstemp(dir=test_directory)
                
                untracked_path = test_directory / untracked_path
                modified_path = test_directory / modified_path
                deleted_path = test_directory / deleted_path
                
                repository.add_index([
                    modified_path.as_posix(),
                    deleted_path.as_posix(),
                ])
                modified_path.write_bytes(b"modified content")
                deleted_path.unlink()
                
                status_command()
                
                assert "On branch main" in mock_stdout.getvalue()
                assert "unstaged" in mock_stdout.getvalue()
                assert "untracked" in mock_stdout.getvalue()
                assert f"modified: {modified_path.relative_to(test_directory.parent)}" in mock_stdout.getvalue()
                assert f"deleted: {deleted_path.relative_to(test_directory.parent)}" in mock_stdout.getvalue()
                assert f"new file: {untracked_path.relative_to(test_directory.parent)}" in mock_stdout.getvalue()

    